from common.models.folktale import AnnotatedFolktale
from common.utils.regex_utils import title_case_to_snake_case
from matplotlib.figure import Figure
from loguru import logger
import pandas as pd
import json
import os

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

def load_txt_folder(dir: str):
	files = {}
	for file in os.listdir(dir):
		if file.endswith(".txt"):
			filename = os.path.splitext(file)[0]

			path = os.path.join(dir, file)
			with open(path, "r", encoding="utf-8") as f:
				text = f.read()
			files[filename] = text
	return files

data_dir = "./data"

def load_folktale_csv():
	file = "folk_tales_deduplicated.csv"
	path = os.path.join(data_dir, file)

	df = pd.read_csv(path)

	logger.info(df.head())
	
	return df

out_dir = "./out"

def save_annotated_folktale(folktale: AnnotatedFolktale, filename: str):
	annotated_dir = os.path.join(out_dir, "annotated")

	os.makedirs(annotated_dir, exist_ok=True)

	folktale_json = folktale.model_dump(
		mode="json",
		exclude_none=True
	)

	output_file = title_case_to_snake_case(filename) + ".json"
	path = os.path.join(annotated_dir, output_file)

	with open(path, "w", encoding="utf-8") as f:
		json.dump(folktale_json, f, ensure_ascii=False, indent=4)

	logger.info(f"Annotated folktale saved sucessfully. Filename: {os.path.basename(path)}.")

def save_raw_folktale(folktale: str, filename: str):
	raw_dir = os.path.join(out_dir, "raw")

	os.makedirs(raw_dir, exist_ok=True)

	output_file = title_case_to_snake_case(filename) + ".txt"
	path = os.path.join(raw_dir, output_file)

	with open(path, "w", encoding="utf-8") as f:
		f.write(folktale)
	
	logger.info(f"Raw folktale saved sucessfully. Filename: {os.path.basename(path)}.")

def save_fig(fig: Figure, filename: str):
	fig.savefig(filename, dpi=300, bbox_inches="tight")
