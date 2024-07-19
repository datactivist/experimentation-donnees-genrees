# Expérimentation Données Genrées

Une expérimentation sur la part des données genrées en Open Data, inspiré du travail "Gender Data Gap" à Berlin.  
Une traduction de l'article en français est disponible via le fichier `Gender Data und Open Data Berlin.pdf`.

## Installation

Installation des dépendances :

Créer un environnement virtuel :

```sh
python -m venv env
```

Activer l'environnement virtuel :

```sh
env\Scripts\activate # Windows
source env/bin/activate # Linux
```

Installer les dépendances dans l'environnement virtuel :

```sh
pip install -r requirements.txt
```

## Utilisation

Extraire les données via l'API d'ODS :

```sh
python extract_ods_datasets.py
```

Filtrer les données afin de recueillir les statistiques sur les données genrées :

```sh
python filter_datasets.py
```

## Résultats

Les fichiers de sorties sont disponibles dans le dossier `data/processed`.  
Ils correspondent aux datasets détectés comme concernant des personnes physiques, ou genrés.  
Leurs contenu peut être déduit de leurs noms :

### Méthode de détection

Si le préfixe `only_legacy_` est présent, cela signifie que la détéction n'a été faite que via la méthode de Berlin : en regardant la description des datasets.
Si le préfixe `only_field_` est présent, cela signifie que la détéction n'a été faite que via notre nouvelle méthode permise par l'API d'ODS : en regardant le nom des champs des datasets.
Si le préfixe `both_` est présent, cela signifie que la détéction a été faite via les deux méthodes.

### Type de datasets

Ensuite, si le terme `gendered` est présent, cela concerne les datasets détectés comme genrés.  
Si le terme `person` est présent, cela concerne les datasets détectés comme concernant des personnes physiques.

Le fichier `person_gendered_datasets.csv` contient les datasets détectés comme genrés **et** concernant des personnes physiques via les **deux** méthodes.

### Statistiques basiques

Quelques statistiques pour notre itération (19/07/2024) :

- Données genrées prédites par la méthode de Berlin : `1204/30000 (4.01%)`
- Données genrées prédites par notre méthode : `1535/30000 (5.12%)`
- Données genrées prédites par les deux méthodes : `715`

- Données concernant des personnes prédites par la méthode de Berlin : `3664/30000 (12.21%)`
- Données concernant des personnes prédites par notre méthode : `1463/30000 (4.88%)`
- Données concernant des personnes prédites par les deux méthodes : `683`

Cela donne un total de `2024/30000` datasets détectés comme genrés (6.75%)
Si on ne considère que les datasets détectés comme concernant des personnes : `1054/4444` datasets genrés (23.72%)
