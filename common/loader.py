import os
import pandas as pd

data_dir = "./data"

def load_folktales():
    file = "folk_tales_deduplicated.csv"
    path = os.path.join(data_dir, file)

    df = pd.read_csv(path)

    print(df.head())

    return df