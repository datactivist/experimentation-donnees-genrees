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

EXACT_GENDER_DETECTION_KEYWORDS = [
    "h",
    "m",
    "man",
    "men",
]  # Keywords that need to be an exact match and not just a substring

GENDER_DETECTION_KEYWORDS = [
    "homme",
    "hommes",
    "femme",
    "femmes",
    "woman",
    "women",
    "sexe",
    "sexes",
    "sex",
    "genre",
    "genres",
    "gender",
    "fille",
    "filles",
    "garçon",
    "garçons",
    "girl",
    "girls",
    "boy",
    "boys",
    "non binaire",
]

PERSON_DETECTION_KEYWORDS = [
    "person",
    "people",
    "personne",
    "personnes",
    "individu",
    "individus",
    "individual",
    "individuals",
    "citoyen",
    "citoyens",
    "citoyenne",
    "citoyennes",
    "citizen",
    "citizens",
    "âge",
    "date de naissance",
    "date of birth",
    "salaire",
    "salary",
    "income",
]


def load_datasets():
    """Load the datasets from the datasets.json file.
    Exits if the file does not exist.
    """

    if not (DATA_RAW_DIR / "datasets.json").exists():
        print(
            f"{DATA_RAW_DIR / 'datasets.json'} file does not exist. Please run the extract_ods_datasets.py script first."
        )
        exit(1)

    with open(DATA_RAW_DIR / "datasets.json", "r") as f:
        datasets = json.load(f)

    return datasets


def is_person_dataset_legacy(dataset):
    """Check if the dataset is person-based based on the title and description only.
    Uses keywords defined in PERSON_DETECTION_KEYWORDS.

    Parameters
    ----------
    dataset : dict
        The dataset to check

    Returns
    -------
    bool
        True if the dataset is person-based, False otherwise
    """

    title = dataset["metas"]["default"]["title"]
    title = title.lower() if title else ""

    description = dataset["metas"]["default"]["description"]
    description = description.lower() if description else ""

    title_description = title + " " + description

    if any(kw in title_description for kw in PERSON_DETECTION_KEYWORDS):
        return True

    return False


def is_person_dataset(dataset):
    """Check if the dataset is person-based based on the fields of the dataset.
    Uses keywords defined in PERSON_DETECTION_KEYWORDS.

    Parameters
    ----------
    dataset : dict
        The dataset to check

    Returns
    -------
    bool
        True if the dataset is person-based, False otherwise
    """

    for field in dataset["fields"]:

        label = field["label"] if field["label"] else field["name"]
        label = label.lower().replace("_", " ")

        if any(kw in label for kw in PERSON_DETECTION_KEYWORDS):
            return True

    return False


def is_genedered_dataset_legacy(dataset):
    """Check if the dataset is gendered based on the title and description only.
    Uses keywords defined in GENDER_DETECTION_KEYWORDS.

    Parameters
    ----------
    dataset : dict
        The dataset to check

    Returns
    -------
    bool
        True if the dataset is gendered, False otherwise
    """

    title = dataset["metas"]["default"]["title"]
    title = title.lower() if title else ""

    description = dataset["metas"]["default"]["description"]
    description = description.lower() if description else ""

    title_description = title + " " + description

    if any(kw in title_description for kw in GENDER_DETECTION_KEYWORDS):
        return True

    return False


def is_gendered_dataset(dataset):
    """Check if the dataset is gendered based on the fields of the dataset.
    Uses keywords defined in EXACT_GENDER_DETECTION_KEYWORDS and GENDER_DETECTION_KEYWORDS

    Parameters
    ----------
    dataset : dict
        The dataset to check

    Returns
    -------
    bool
        True if the dataset is gendered, False otherwise
    """

    for field in dataset["fields"]:

        label = field["label"] if field["label"] else field["name"]
        label = label.lower().replace("_", " ")

        if any(kw in label for kw in GENDER_DETECTION_KEYWORDS):
            return True

        if any(kw == label for kw in EXACT_GENDER_DETECTION_KEYWORDS):
            return True

    return False


def format_dataset_csv(datasets_uids, datasets):

    dataframe_data = []

    for dataset in datasets:

        if dataset["dataset_uid"] not in datasets_uids:
            continue

        dataframe_data.append(
            {
                "id": dataset["dataset_id"],
                "url": f"https://data.opendatasoft.com/explore/dataset/{dataset['dataset_id']}/information/",
                "title": dataset["metas"]["default"]["title"],
                "description": dataset["metas"]["default"]["description"],
                "theme": dataset["metas"]["default"]["theme"],
                "publisher": dataset["metas"]["default"]["publisher"],
            }
        )

    return pd.DataFrame(dataframe_data)


if __name__ == "__main__":

    datasets = load_datasets()

    legacy_person_datasets_ids = set()
    person_datasets_ids = set()

    legacy_gendered_datasets_ids = set()
    gendered_datasets_ids = set()

    for dataset in datasets:

        if is_person_dataset_legacy(dataset):
            legacy_person_datasets_ids.add(dataset["dataset_uid"])

        if is_person_dataset(dataset):
            person_datasets_ids.add(dataset["dataset_uid"])

        if is_genedered_dataset_legacy(dataset):
            legacy_gendered_datasets_ids.add(dataset["dataset_uid"])

        if is_gendered_dataset(dataset):
            gendered_datasets_ids.add(dataset["dataset_uid"])

    # person
    both_person_datasets_ids = legacy_person_datasets_ids.intersection(
        person_datasets_ids
    )
    every_person_datasets_ids = legacy_person_datasets_ids.union(person_datasets_ids)

    legacy_person_datasets_df = format_dataset_csv(legacy_person_datasets_ids, datasets)
    legacy_person_datasets_df.to_csv(
        DATA_PROCESSED_DIR / "only_legacy_person_datasets.csv"
    )
    person_datasets_df = format_dataset_csv(person_datasets_ids, datasets)
    person_datasets_df.to_csv(DATA_PROCESSED_DIR / "only_field_person_datasets.csv")
    both_person_datasets_df = format_dataset_csv(both_person_datasets_ids, datasets)
    both_person_datasets_df.to_csv(DATA_PROCESSED_DIR / "both_person_datasets.csv")
    every_gendered_datasets_df = format_dataset_csv(every_person_datasets_ids, datasets)

    # gendered
    both_gendered_datasets_ids = legacy_gendered_datasets_ids.intersection(
        gendered_datasets_ids
    )
    every_gendered_datasets = legacy_gendered_datasets_ids.union(gendered_datasets_ids)
    legacy_gendered_datasets_df = format_dataset_csv(
        legacy_gendered_datasets_ids, datasets
    )
    legacy_gendered_datasets_df.to_csv(
        DATA_PROCESSED_DIR / "only_legacy_gendered_datasets.csv"
    )
    gendered_datasets_df = format_dataset_csv(gendered_datasets_ids, datasets)
    gendered_datasets_df.to_csv(DATA_PROCESSED_DIR / "only_field_gendered_datasets.csv")
    both_gendered_datasets_df = format_dataset_csv(both_gendered_datasets_ids, datasets)
    both_gendered_datasets_df.to_csv(DATA_PROCESSED_DIR / "both_gendered_datasets.csv")

    person_gendered_datasets_ids = every_person_datasets_ids.intersection(
        every_gendered_datasets
    )
    person_gendered_datasets_df = format_dataset_csv(
        person_gendered_datasets_ids, datasets
    )
    person_gendered_datasets_df.to_csv(
        DATA_PROCESSED_DIR / "person_gendered_datasets.csv"
    )

    print(
        f"- Données genrées prédites par la méthode de Berlin : `{len(legacy_gendered_datasets_ids)}/{len(datasets)} ({len(legacy_gendered_datasets_ids)/len(datasets):.2%})`"
    )
    print(
        f"- Données genrées prédites par notre méthode : `{len(gendered_datasets_ids)}/{len(datasets)} ({len(gendered_datasets_ids)/len(datasets):.2%})`"
    )
    print(
        f"- Données genrées prédites par les deux méthodes : `{len(both_gendered_datasets_ids)}`"
    )

    print(
        f"- Données concernant des personnes prédites par la méthode de Berlin : `{len(legacy_person_datasets_ids)}/{len(datasets)} ({len(legacy_person_datasets_ids)/len(datasets):.2%})`"
    )
    print(
        f"- Données concernant des personnes prédites par notre méthode : `{len(person_datasets_ids)}/{len(datasets)} ({len(person_datasets_ids)/len(datasets):.2%})`"
    )
    print(
        f"- Données concernant des personnes prédites par les deux méthodes : `{len(both_person_datasets_ids)}`"
    )

    print(
        f"Cela donne un total de `{len(every_gendered_datasets)}/{len(datasets)}` datasets détectés comme genrés ({len(every_gendered_datasets)/len(datasets):.2%})"
    )
    print(
        f"Si on ne considère que les datasets détectés comme concernant des personnes : `{len(person_gendered_datasets_ids)}/{len(every_person_datasets_ids)}` datasets genrés ({len(person_gendered_datasets_ids)/len(every_person_datasets_ids):.2%})"
    )
