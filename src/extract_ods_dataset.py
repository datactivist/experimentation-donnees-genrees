import requests
from dotenv import dotenv_values
import os
import json
from pathlib import Path
import pandas as pd

config = {
    **dotenv_values(".env.shared"),  # load shared development variables
    **os.environ,  # override with current environment variables
    **dotenv_values(".env"),  # override with .env environment variables
}

DATA_RAW_DIR = Path(config["DATA_RAW_DIR"])
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

DATA_PROCESSED_DIR = Path(config["DATA_PROCESSED_DIR"])
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

ODS_API_URL = config["ODS_API_URL"]


def extract_datasets():

    limit = 100
    offset = 0

    datasets = []

    while True:

        print(f"Fetching datasets from offset {offset} to {offset + limit}...")
        # undocumented restriction : offset + limit must be below 30000

        response = requests.get(
            f"{ODS_API_URL}/catalog/datasets?limit={limit}&offset={offset}"
        )

        if not response.ok:

            with open(DATA_RAW_DIR / f"datasets.json", "w") as f:
                json.dump(datasets, f, indent=2)

            response.raise_for_status()

            break

        results = response.json()

        if not results.get("results", []):
            break

        datasets += results.get("results", [])
        offset += limit

        if offset % 5000 == 0:
            print(f"Saving datasets checkpoint at offset {offset}...")
            with open(DATA_RAW_DIR / f"datasets-checkpoint-{offset}.json", "w") as f:
                json.dump(datasets, f, indent=2)

    return datasets


if __name__ == "__main__":

    datasets = extract_datasets()

    with open(DATA_RAW_DIR / "datasets.json", "w") as f:
        json.dump(datasets, f, indent=2)

    print(f"Extracted {len(datasets)} datasets")
