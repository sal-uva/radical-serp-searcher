import config
import requests
import time
import json
from datetime import datetime

from helpers import query_to_search_url


def queue_screenshots_via_4cat(questions, search_engine="google"):
	"""

	Queues 4CAT's screenshot generator: https://github.com/digitalmethodsinitiative/4cat_web_studies_extensions/tree/main/datasources/url_screenshots

	"""

	timestamp = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d_%H:%M")
	print(f"Generating {len(questions)} screenshots of the {search_engine} SERP at {timestamp}")

	query_questions = []
	for question in questions.values():
		query_questions.append(query_to_search_url(question["question_simplified_contextualized"], search_engine=search_engine))

	if not query_questions:
		print("No questions above the thresholds")
		quit()

	ignore_cookies = True
	if "bing" in search_engine:
		ignore_cookies = False

	query_4cat = {
		"datasource": "image-downloader-screenshots",
		"query": "\n".join(query_questions),
		"capture": "all",
		"wait-time": config.SELENIUM_WAIT_TIME,
		"resolution": config.SELENIUM_RESOLUTION,
		"pause-time": config.SELENIUM_PAUSE_TIME,
		"ignore-cookies": ignore_cookies,
		"frontend-confirm": True,
		"label": f"serp-screenshots_{search_engine}_{timestamp}"
	}

	url_4cat = config.URL_4CAT + "/api/queue-query"
	headers = {"Authentication": config.TOKEN_4CAT}

	retries = 0
	max_retries = 5
	snooze_time = 5
	response = None

	while retries <= max_retries:
		try:
			response = requests.post(url_4cat, data=query_4cat, headers=headers)
		except Exception as e:
			print(e)
			retries += 1
			time.sleep(snooze_time)

	if not response:
		print("Couldn't connect to 4CAT, see errors above")

	if response.status_code == 500:
		print("4CAT encountered a server error, contact the admins")
		quit()

	response_msg = response.json()

	if response_msg["status"] == "error":
		print(f"4CAT can't process the screenshots: {response_msg}")
		quit()

	elif response_msg["status"] == "success":
		dataset_url = config.URL_4CAT + "/results/" + response_msg["key"]
		print(f"Started screenshot capturing at {dataset_url}")
