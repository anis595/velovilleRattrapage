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

## Tests et couverture

Depuis la racine du projet, exécuter :

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=api/services --cov-report=term-missing
```

Résultat obtenu : 99 tests réussis et 78 % de couverture des modules
`api/services`.

## Choix écoresponsables

- Les listes sont paginées côté serveur, avec une taille limitée à 100 éléments. L'API ne transmet que la page demandée.
- Le front ne se rafraîchit pas automatiquement. Les indicateurs sont actualisés quand l'utilisateur agit sur les filtres ou sur le bouton « Actualiser ».
- La liste des communes est mise en cache pendant une heure avec `st.cache_data`, ce qui évite de relire toutes les stations à chaque affichage.
- Les indicateurs sont agrégés en SQL dans PostgreSQL ; le front reçoit les résultats déjà calculés.
