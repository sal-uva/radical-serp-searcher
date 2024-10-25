import json
import base64
import glob

from collections import Counter

from openai import OpenAI

import config
from prompts import SERP_INTERFACE_PROMPTS


def encode_image(image_path):
	with open(image_path, "rb") as image_file:
		return base64.b64encode(image_file.read()).decode('utf-8')


def get_interface_elements(path_to_image: str, search_engine: str) -> list:

	client = OpenAI(api_key=config.OPENAI_KEY)

	# Getting the base64 string
	base64_image = encode_image(path_to_image)
	img_url = f"data:image/png;base64,{base64_image}"

	prompt = SERP_INTERFACE_PROMPTS.replace("[SEARCH_ENGINE]", search_engine)

	response = client.chat.completions.create(
		model=config.VISION_MODEL,
		response_format={"type": "json_object"},
		messages=[
			{
				"role": "user",
				"content": [
					{
						"type": "text",
						"text": prompt
					},
					{
						"type": "image_url",
						"image_url": {
							"url": img_url,
							"detail": "high"
						},
					}
				]
			}
		],
		max_tokens=3000,
	)

	return json.loads(response.choices[0].message.content)

def get_interface_element_counts(in_dir: str) -> Counter:

	all_elements = []
	for f in glob.glob(in_dir + "/*.json"):
		elements = json.load(open(f, "r"))
		all_elements += list(elements.keys())

	return Counter(all_elements)


if __name__ == "__main__":

	i = 0
	for f in glob.glob("data/serp-images-for-interface-extraction/google/*.png"):
		out_name = f[:-4] + ".json"
		if out_name in glob.glob("data/serp-images-for-interface-extraction/google/*.json"):
			continue
		i_e = get_interface_elements(f, "google")

		with open(f[:-4] + ".json", "w") as out_json:
			json.dump(i_e, out_json)

		i += 1
		if i >= 100:
			break

	print("processing Google images")
	print(get_interface_element_counts("data/serp-images-for-interface-extraction/google/"))

	image_files = "data/serp-images-for-interface-extraction/google/*.png"
