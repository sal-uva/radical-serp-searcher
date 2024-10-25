import os
import openai
import html2text
import hashlib
import re

from typing import Generator

import config


def make_dirs():

	# Make dirs
	if not os.path.isdir("data"):
		os.mkdir("data")

	if not os.path.isdir("data/catalogs"):
		os.mkdir("data/catalogs")
	for board in list(config.CATALOGS.keys()):
		if not os.path.isdir("data/catalogs/" + board):
			os.mkdir("data/catalogs/" + board)


def questions_above_thresholds(questions: dict) -> dict:
	"""
	Returns questions above the threshold set in config.py.
	"""

	print("Filtering questions for those above the set thresholds")
	print(f"  {len(questions)} questions before filtering")

	questions = {k: v for k, v in questions.items() if
				 v["count"] >= config.QUESTION_THRESHOLD and
				(v["explicit"] if config.MUST_BE_EXPLICIT else True)
				 and v["TOXICITY"] >= config.MIN_TOXICITY}

	print(f"  {len(questions)} questions after filtering")
	return questions


def chunker(seq: list, size: int) -> Generator:
	"""
	Used for feeding data in chunks to LLMs.
	"""
	return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def get_openai_answer(prompt: str, response_format="json_object", model=None):
	# initiate
	client = openai.OpenAI(api_key=config.OPENAI_KEY)

	if not model:
		model = config.MODEL

	# Get response
	response = client.chat.completions.create(
		model=model,
		temperature=config.TEMPERATURE,
		max_tokens=config.MAX_OUTPUT_TOKENS,
		response_format={"type": response_format},
		messages=[{
			"role": "user",
			"content": prompt
		}]
	)

	return response.choices[0].message.content


def clean_and_hash(input_string: str) -> str:
	"""
	Remove all special characters (except accents)
	and non-numeric, non-letter characters.
	"""
	input_string = input_string.lower().strip()
	input_string = re.sub(r"[^0-9A-Za-zÀ-ÿ]", "", input_string)

	# Then hash the string so we can match them.
	encoded_string = input_string.encode('utf-8')
	hash_object = hashlib.sha256(encoded_string)
	hex_dig = hash_object.hexdigest()
	return hex_dig


def clean_html(html_string: str) -> str:
	"""
	Clean up a HTML string.
	"""
	h = html2text.HTML2Text()

	# Don't wrap lines!
	h.body_width = 0

	cleaned = h.handle(html_string)

	if not cleaned:
		cleaned = ""

	return cleaned


def query_to_search_url(query: str, search_engine="google") -> str:
	"""
	Converts a string query to a search engine query URL

	"""

	query = query.lower().strip().replace(" ", "+")

	search_engine = search_engine.lower()
	if search_engine == "google":
		return f"https://www.google.com/search?q={query}"
	elif search_engine == "duckduckgo":
		return f"https://www.duckduckgo.com/?q={query}"
	elif search_engine == "bing":
		return f"https://www.bing.com/search?q={query}"
	elif search_engine == "yahoo":
		return f"https://www.yahoo.com/search?q={query}"
	elif search_engine == "yandex":
		return f"https://www.yandex.com/search?q={query}"
	else:
		raise Exception("Search engine not supported")