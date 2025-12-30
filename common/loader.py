import os
import json
import pandas as pd
from loguru import logger

data_dir = "./data"

def load_folktales():
    file = "folk_tales_deduplicated.csv"
    path = os.path.join(data_dir, file)

    df = pd.read_csv(path)

    logger.info(df.head())
    
    return df

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

def load_json_folder(dir: str):
    folder_path = os.path.join(data_dir, dir)

    files = {}
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            filename = os.path.splitext(file)[0]

            path = os.path.join(folder_path, file)
            json = load_json(path)
            files[filename] = json
    return files

# def load_hierarchies():
#     hierarchy_directory = "hierarchies/"
#     hiearchy_path = os.path.join(data_dir, hierarchy_directory)

#     hierarchies = {}
#     for file in os.listdir(hiearchy_path):
#         if file.endswith(".json"):
#             filename = os.path.splitext(file)[0]

#             path = os.path.join(hiearchy_path, file)
#             hierarchy = load_json(path)
#             hierarchies[filename] = hierarchy
#     return hierarchies

# def load_examples():
#     examples_dir = "examples/"
#     examples_path = os.path.join(data_dir, examples_dir)

#     folktales = []
#     for file in os.listdir(examples_path):
#         if file.endswith(".json"):
#             filename = os.path.splitext(file)[0]

#             path = os.path.join(examples_path, file)
#             folktale = load_json(path)
#             folktales.append(folktale)
#     return folktales