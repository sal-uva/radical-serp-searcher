"""
EXECUTE THIS EVERY X HOURS!

Schedules the following tasks:
1. Get chan catalogs (`get_chan_catalogs.py`)
2. Extract, manipulate, and rank questions (`chan_questions.py`)
3. Search the questions on Google and Bing and take a screenshot via 4CAT (`serp_screenshots.py`)
~~4. Analyse these screenshots (`serp_screenshots.py`)~~

INSERT YOUR SETTINGS AT CONFIG.PY (see config-example.py for an example)

"""

import chan_catalogs
import chan_questions
import json
import glob

import config
import serp_screenshots

from helpers import make_dirs, questions_above_thresholds


if __name__ == '__main__':

	# Prep work
	make_dirs()

	if config.COLLECT_CATALOGS:
		# Retrieve catalogs
		chan_catalogs.collect()

	if config.PROCESS_QUESTIONS:
		# Extract questions for all catalog files that haven't been processed yet
		unprocessed_catalog_files = []
		processed_files = glob.glob("data/catalogs/**/*.json")
		for f in processed_files:
			file_name = f.split(".")[-2] + ".csv"
			if file_name not in processed_files and "questions" not in file_name:
				unprocessed_catalog_files.append(f)

		# Get questions from OPs and manipulate them with LLMs
		for unprocessed_catalog_file in unprocessed_catalog_files:
			chan_questions.process(unprocessed_catalog_file)

	if config.TAKE_SCREENSHOTS:
		# Retrieve extracted questions
		with open("data/questions.json", "r") as in_json:
			questions = json.load(in_json)

		# Only keep those above set threshold in config
		questions = questions_above_thresholds(questions)

		if questions:
			# Generate screenshots via 4CAT
			for search_engine in config.SEARCH_ENGINES:
				serp_screenshots.queue_screenshots_via_4cat(questions, search_engine=search_engine)

	print("Done (for now)")
