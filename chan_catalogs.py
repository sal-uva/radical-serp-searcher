# -*- coding: utf-8 -*-
import time
import json
import requests

import config


def collect():
	"""
	Code to retrieve the catalog pages of imageboards.
	Saves the `catalog.json` endpoints without processing them.
	These should be defined in `config.py`.

	"""

	catalogs = config.CATALOGS

	for catalog_url in catalogs:

		current_time = int(time.time())
		catalog = []

		try:
			catalog = requests.get(catalog_url).json()
		except Exception as e:
			print(e)

		imgboard = "undefined"
		if "leftypol" in catalog_url:
			imgboard = "leftypol"
		elif "4cdn" in catalog_url:
			imgboard = "4chanpol"

		out_name = f"data/catalogs/{imgboard}/{current_time}.json"

		if catalog:
			with open(out_name, "w", encoding="utf-8") as f:
				f.write(json.dumps(catalog))

		print(f"Retrieved {catalog_url}, saved to {out_name}")