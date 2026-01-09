from common.models.folktale import AnnotatedFolktale
from common.utils.loader import save_structured_folktale
from loguru import logger
import os

out_dir = "./generation/out"

def save_annotated_folktale(folktale: AnnotatedFolktale, filename: str):	
	annotated_dir = os.path.join(out_dir, "annotated")

	save_structured_folktale(folktale, annotated_dir, filename)
	
def save_raw_folktale(folktale: str, filename: str):
	raw_dir = os.path.join(out_dir, "raw")

	os.makedirs(raw_dir, exist_ok=True)

	output_file = filename + ".txt"
	path = os.path.join(raw_dir, output_file)

	with open(path, "w", encoding="utf-8") as f:
		f.write(folktale)
	
	logger.debug(f"Raw folktale saved sucessfully. Filename: {os.path.basename(path)}.")