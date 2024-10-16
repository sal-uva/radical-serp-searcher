# -*- coding: utf-8 -*-
"""

This script:
1. Gets questions from catalog posts
  - Get subject and body texts from openings posts (OPs). These are posts where fully phrased questions are often posed.
  - Extract the sentences ending with a question mark.
  - Remove questions that are longer than 150 characters.
2. Determine whether the questions are explicit or not
  - I.e. if you'd use them in a search engine
3. Simplify and homogenise the questions (extract grammatical features)
4. Scores the questions with Perplexity API.
5. Queries the phrases on Google and Bing

Chunker so we can feed content to the LLM in chunks:
"""
import json
import re
import os
import time
import pandas as pd

from collections import Counter
from googleapiclient.errors import HttpError
from googleapiclient import discovery

import config
import prompts

from helpers import get_openai_answer, chunker, clean_and_hash, clean_html


def extract_questions(string: str) -> list:
	"""
	Split a string intro sentences, return those ending with a question mark.
	"""

	sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=[.?!\n])\s', string)
	questions = []

	for sentence in sentences:

		# Strip, but keep capital letters so LLMs can infer meaning from them.
		sentence = sentence.strip()

		if sentence.endswith("?"):
			questions.append(sentence)

	# Only unique questions
	questions = list(set(questions))

	return questions


def simplify_and_contextualise_questions(string: str) -> dict:
	"""
	Simplify and contextualise questions through LLMs.

	The prompt asks to:
	1. Simplify a question.
	2. Contextualize it by resolving implicit references (e.g. "they" or "she").
	3. Extract a subject from the sentence.

	Uses OpenAI.
	"""

	prompt = prompts.SIMPLIFY_AND_CONTEXTUALISE
	answer = get_openai_answer(prompt.replace("[input]", string))

	questions_simple = json.loads(answer)["results"]
	return questions_simple


def score_explicit_question(string: str) -> list:
	"""
	Uses LLMs to score a question based on whether it is considered explicit or implicit.

	Uses OpenAI.

	"""

	prompt = prompts.IS_EXPLICIT

	answer = get_openai_answer(prompt.replace("[input]", string))

	results = json.loads(answer)["results"]
	return results


def get_toxicity_scores(texts: list) -> list:
	"""
	Score texts with toxicity scores through Google Jigsaw's Perspective API.
	"""

	# Create client
	api_key = config.GOOGLE_KEY

	try:
		client = discovery.build(
			"commentanalyzer",
			"v1alpha1",
			developerKey=api_key,
			discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
			static_discovery=False,
		)
	except HttpError as e:
		error = json.loads(e.content)["error"]["message"]
		raise Exception(error)

	results = []

	attributes = ["TOXICITY", "SEVERE_TOXICITY", "IDENTITY_ATTACK", "INSULT", "PROFANITY", "THREAT"]
	api_attributes = {attribute: {} for attribute in attributes}

	i = 0

	for text in texts:
		analyze_request = {
			"comment": {"text": text},
			"requestedAttributes": api_attributes
		}

		try:
			response = client.comments().analyze(body=analyze_request).execute()
		except HttpError as e:
			raise Exception(e)

		result = {}
		for attribute in attributes:
			result[attribute] = float(response["attributeScores"][attribute]["summaryScore"]["value"])

		results.append(result)
		i += 1
		print(f"  Scored {i}/{len(texts)} questions")

		# Don't exceed the rate limit
		time.sleep(1)

	return results


def parse_ops_from_catalog(in_catalog: list) -> list:
	"""
	Extracts only the relevant OP data from a catalog file.
	"""

	ops = []

	for page in in_catalog:
		for thread in page["threads"]:
			op = {
				"id": thread["no"],
				"timestamp_utc": thread["time"],
				"title": clean_html(thread.get("sub", "")),
				"body": clean_html(thread.get("com", "")),
				"replies": thread["replies"],
				"board": thread.get("board", "")
			}

			ops.append(op)

	return ops


def process(catalog_file: str):
	"""

	Take a catalog file and run through the whole processing step.

	Only processes posts that haven't been processed already.
	Processed IDs are stored in `data/processed_ids.json` and
	a full list of extracted and manipulated questions will be found in `data/questions.json` and `data/questions.csv`.

	"""
	print("Processing " + catalog_file)
	catalog = json.load(open(catalog_file))
	ops = parse_ops_from_catalog(catalog)

	# Only keep OPs that generated X replies
	ops = [op for op in ops if op["replies"] >= config.MIN_REPLIES]
	print(f"  Kept {len(ops)} OPs with {config.MIN_REPLIES} or more replies")

	# Extract questions
	for i in range(len(ops)):
		ops[i]["questions"] = extract_questions(ops[i]["title"] + "\n" + ops[i]["body"])

	# Only keep OPs with questions
	ops = [op for op in ops if op["questions"]]
	print(f"  Kept {len(ops)} OPs with questions")

	# Skip OPs with questions and enough replies that we've processed before
	processed_ops_json = "data/processed_ids.json"
	if not os.path.isfile(processed_ops_json):
		json.dump([], open(processed_ops_json, "w"))
	processed_ops = json.load(open(processed_ops_json))
	ops = [op for op in ops if op["id"] not in processed_ops]
	print(f"  Kept {len(ops)} OPs that we haven't processed before")

	if not ops:
		return

	# Create a dictionary *per question* instead of per OP
	questions = []
	for op in ops:
		for question in op["questions"]:
			# Use the original data
			q_op = op.copy()
			q_op["question"] = question
			# Remove *all* questions
			if "questions" in q_op:
				del q_op["questions"]
			questions.append(q_op)

	# Get rid of overly long questions that mess up the token length
	questions = [q for q in questions if len(q["question"]) < config.MAX_QUESTION_LENGTH]
	print(f"  {len(questions)} questions extracted")

	if not questions:
		return

	# Slice if we're debugging
	if config.DEBUG_LENGTH:
		questions = questions[:config.DEBUG_LENGTH]

	# SIMPLIFY, CONTEXTUALISE, AND EXTRACT SUBJECT
	print(f"Simplifying {len(questions)} questions")
	i = 0
	for q_chunk in chunker(questions, config.CHUNKS):

		retries = 0

		# Keep looping until we have the same amount of input v output results
		while retries < config.MAX_OPENAI_RETRIES:
			questions_flat = json.dumps([
				{
					"question": q["question"],
					"full_text": q["title"] + "\n" + q["body"]
				} for q in q_chunk])

			questions_simple = simplify_and_contextualise_questions(questions_flat)

			# Check if the input and output length is the same
			if len(questions_simple) != len(q_chunk):
				print(f"  The LLM output is not the same length as the input ({len(questions_simple)} vs {len(q_chunk)}). Trying again.")
				retries += 1
				continue

			# Add to original dataset
			for q_simple in questions_simple:
				questions[i]["question_simplified_contextualized"] = q_simple["question_simplified_contextualized"]
				subject = q_simple.get("subject", "")
				if subject:
					questions[i]["subject"] = subject.lower().strip()
				else:
					questions[i]["subject"] = ""
				i += 1

			print(f"  Simplified {i}/{len(questions)} questions")
			break

		time.sleep(1)

	# SCORE EXPLICITNESS
	print(f"Categorizing whether {len(questions)} questions are explicit or not.")
	i = 0
	for q_chunk in chunker(questions, config.CHUNKS):

		retries = 0

		while retries < config.MAX_OPENAI_RETRIES:

			questions_flat = "\n".join([q.get("question_simplified_contextualized", "") for q in q_chunk])
			scored_questions = score_explicit_question(questions_flat)

			# Check if the input v output length is the same
			if len(scored_questions) != len(q_chunk):
				print(
					f"  The LLM output is not the same length as the input ({len(scored_questions)} vs {len(q_chunk)}). Trying again.")
				retries += 1
				continue

			for scored_question in scored_questions:
				questions[i]["explicit"] = scored_question["explicit"]
				i += 1

			print(f"  Categorized {i}/{len(questions)} questions as explicit/implicit")
			break

	# SCORE WITH PERSPECTIVE API
	print(f"Scoring {len(questions)} questions with toxicity scores")
	questions_input = [q["question_simplified_contextualized"] for q in questions]
	toxicity_scores = get_toxicity_scores(questions_input)
	for i in range(len(questions)):
		questions[i]["toxicity"] = toxicity_scores[i]

	# SAVE AS CATALOG-SPECIFIC JSON AND CSV
	catalog_filename = catalog_file[:-5] + "_questions"
	with open(f"{catalog_filename}.json", "w", encoding="utf-8") as out_json:
		json.dump(questions, out_json)
	df = pd.DataFrame(questions)
	df.to_csv(f"{catalog_filename}.csv", index=False)

	# THEN MERGE WITH PROCESSED DATA AND RANK
	# Save what IDs we've processed (with valid questions or not)
	op_ids = [op["id"] for op in ops]
	processed_ids = list(set(processed_ops + op_ids))
	with open(processed_ops_json, "w") as out_json:
		json.dump(processed_ids, out_json)

	# Also save a JSON and CSV on *all* questions
	questions_json_file = "data/questions.json"
	questions_csv_file = "data/questions.csv"

	all_questions = {}
	if os.path.isfile(questions_json_file):
		all_questions = json.load(open(questions_json_file, "r"))

	# Get a hash of the simplified question minus special characters as a key.
	# This way we can better group and count the questions.
	questions_hashed = {clean_and_hash(q["question_simplified_contextualized"]): q for q in questions}

	# Merge new questions with old questions.
	# Update stuff like reply counts.
	for question_hash, question in questions_hashed.items():

		# New question
		if question_hash not in all_questions:
			all_questions[question_hash] = {
				"hash": question_hash,
				"question_simplified_contextualized": question["question_simplified_contextualized"],
				"count": 1,
				"replies": question["replies"],
				"pol_count": 1 if "4chan" in catalog_file else 0,
				"leftypol_count": 1 if "leftypol" in catalog_file else 0,
				"subject": question["subject"],
				"subjects_all": [question["subject"]],
				"explicit": question["explicit"],
				"explicit_all": question["explicit"],
				**[question["toxicity"]][0],
				"questions_original": [question["question"]],
				"ids": [question["id"]],
				"timestamps": [question["timestamp_utc"]]
			}

		# Already-encountered question. Update some data!
		else:
			# Add some question data to existing data
			old_question = all_questions[question_hash]

			# Add total question occurrences
			old_question["count"] += 1

			# Add occurrences per board
			if "4chan" in catalog_file:
				old_question["pol_count"] += 1
			if "leftypol" in catalog_file:
				old_question["leftypol_count"] += 1

			# Add to reply count
			old_question["replies"] += question["replies"]

			# Add to subjects, and take the most-occurring subject as the main
			# one (these may slightly differ because of LLM extraction)
			old_question["subjects_all"].append(question["subject"])
			old_question["subject"] = Counter(old_question["subjects_all"]).most_common(1)[0][0]

			# Same for 'explicit'
			old_question["explicit_all"].append(question["explicit"])
			old_question["explicit"] = Counter(old_question["explicit"]).most_common(1)[0][0]

			# Other metadata
			old_question["questions_original"].append(question["question"])
			old_question["ids"].append(question["id"])
			old_question["timestamps"].append(question["timestamp_utc"])

	# Perspective API is deterministic so should remain the same

	# Save as JSON *and* CSV
	with open(questions_json_file, "w", encoding="utf-8") as out_json:
		json.dump(all_questions, out_json)

	df = pd.DataFrame(all_questions.values())
	df.to_csv(questions_csv_file, index=False)