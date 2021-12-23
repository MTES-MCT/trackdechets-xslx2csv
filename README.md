# Xlsx2Csv

Convertisseur de fichiers en ligne de commande pour faciliter les tâches d'import en masse.
Lit, valide et transforme un fichier xlsx en 2 fichiers csv prêts à importer dans Trackdéchets


## Mise en route

### Pré-requis

- Python 3.9 est requis. (Pour gérer plusieurs versions de python [pyenv](https://github.com/pyenv/pyenv) est recommandé)
- [Poetry](https://python-poetry.org) 
- alternativement vous pouvez utiliser pip pour installer les quelques dépendances listées dans pyproject.toml

### Installation

Cloner le projet et installer les dépendances

    git clone git@github.com:MTES-MCT/trackdechets-xslx2csv.git

    cd xlsx2csv

    poetry install

Activer votre environnement
    
    poetry shell

## Utilisation

    python xlsx2csv.py path/to/somefile.xlsx

Par défaut 

    python xlsx2csv.py

Cherchera un fichier file.xlsx dans xlsx2csv/src/

En cas de validation réussie, le menu  propose d'exporter les fichiers csv qui seront créés dans  xlsx2csv/src/csv/

### Aide

    python xlsx2csv.py -h
