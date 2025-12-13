import os
import json

data_dir = "./annotation/data"

def load_json(file: str):
    path = os.path.join(data_dir, file)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data