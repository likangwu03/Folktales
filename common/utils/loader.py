from common.models.folktale import AnnotatedFolktale
from common.utils.regex_utils import title_case_to_snake_case
import os
import json
import pandas as pd
from loguru import logger

def load_json(path: str):
	with open(path, "r", encoding="utf-8") as f:
		data = json.load(f)

	return data

def load_json_folder(dir: str):
	files = {}
	for file in os.listdir(dir):
		if file.endswith(".json"):
			filename = os.path.splitext(file)[0]

			path = os.path.join(dir, file)
			json = load_json(path)
			files[filename] = json
	return files

data_dir = "./data"

def load_folktale_csv():
	file = "folk_tales_deduplicated.csv"
	path = os.path.join(data_dir, file)

	df = pd.read_csv(path)

	logger.info(df.head())
	
	return df

out_dir = "./out"

def save_folktale(folktale: AnnotatedFolktale):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	folktale_json = folktale.model_dump(mode="json")

	output_file = title_case_to_snake_case(folktale.title) + ".json"
	path = os.path.join(out_dir, output_file)

	with open(path, "w", encoding="utf-8") as f:
		json.dump(folktale_json, f, ensure_ascii=False, indent=4)
