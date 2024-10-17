import config
import requests
import time
import json
from datetime import datetime


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
		"wait-time": 6,
		"resolution": "1920x1080",
		"pause-time": 10,
		"ignore-cookies": ignore_cookies,
		"frontend-confirm": True,
		"label": f"serp-screenshots_{search_engine}_{timestamp}"
	}

	url_4cat = config.URL_4CAT + "/api/queue-query"
	headers = {"Authentication": config.TOKEN_4CAT}

	try:
		response = requests.post(url_4cat, data=query_4cat, headers=headers)
	except Exception as e:
		print(e)
		quit()

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
