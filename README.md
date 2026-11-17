# VéloVille — Plateforme de valorisation des données

À compléter : présentation du projet, prérequis, installation, lancement de
l'API et du front, exécution des tests, liens vers la documentation
(docs/), auteur et version.

## Import des données

Depuis la racine du projet, après avoir configuré `DATABASE_URL` dans le
fichier `.env` et créé les tables PostgreSQL, exécuter :

```powershell
python scripts/importer.py
```

Le script lit `data/stations.csv`, `data/trajets.csv` et
`data/incidents.csv`, puis affiche un bilan pour chaque fichier. Il écrit les
rejets, les normalisations et les avertissements dans
`docs/journal-import.csv`. Une nouvelle exécution ne crée pas de doublons.
