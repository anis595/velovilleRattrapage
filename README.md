# VéloVille — Plateforme de valorisation des données

VéloVille lit les fichiers CSV contenant les stations, les trajets et les incidents, puis les charge dans PostgreSQL. Une API FastAPI permet de consulter ces données ainsi que leurs indicateurs. Une interface Streamlit donne accès aux stations, aux incidents et aux indicateurs en fonction du rôle de l’utilisateur.

## Prérequis et installation

Python 3.12, PostgreSQL 14 ou plus récent, ainsi que les outils `psql`, `pg_dump` et `pg_restore`.

Depuis la racine du dépôt, créez un environnement virtuel et installez les dépendances :

```powershell
py -3.12 -m venv .venv
..venv\Scripts\python.exe -m pip install -r requirements.txt
```

Créez la base et un rôle PostgreSQL autorisé à créer des tables. La procédure détaillée se trouve dans la [procédure de déploiement](docs/procedure-deploiement.md). Copiez `.env.example` en `.env`, puis ajustez `DATABASE_URL` et définissez un `JWT_SECRET` personnel. `API_URL` indique l’adresse de l’API pour le front. Le fichier `.env` reste local et n’est pas versionné.

```powershell
Copy-Item .env.example .env
psql -U veloville -d veloville -f sql/schema.sql
```

## Import des données

Depuis la racine du projet, après avoir configuré `DATABASE_URL` dans le fichier `.env` et créé les tables PostgreSQL, lancez :

```powershell
..venv\Scripts\python.exe scripts/importer.py
```

Le script lit `data/stations.csv`, `data/trajets.csv` et `data/incidents.csv`, puis affiche un bilan pour chaque fichier. Il consigne les rejets, les normalisations et les avertissements dans `docs/journal-import.csv`. Une nouvelle exécution ne crée pas de doublons.

## Lancer l'application

Ouvrez deux terminaux dans le dossier du projet. Dans le premier :

```powershell
..venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

Vérifiez [http://127.0.0.1:8000/sante](http://127.0.0.1:8000/sante) ; la réponse attendue est `{"statut":"ok"}`. La documentation interactive se trouve à [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Dans le second terminal :

```powershell
..venv\Scripts\python.exe -m streamlit run front/app.py
```

Le navigateur lance l’interface Streamlit. Les comptes de démonstration sont dans `sql/comptes.sql`. Il faut les insérer dans la base pour pouvoir se connecter. Le rôle `direction` ne fait que consulter les données, le rôle `exploitant` peut aussi changer le statut d’un incident.

## Tests et couverture

Depuis la racine du projet, lancez :

```powershell
..venv\Scripts\python.exe -m pytest --cov=api/services --cov-report=term-missing
```

Le résultat montre 102 tests réussis et 78 % de couverture des modules `api/services`.

## Audit des données

```powershell
..venv\Scripts\python.exe scripts/audit_donnees.py
```

Le script montre les contrôles sur les fichiers CSV sources : valeurs manquantes, doublons, formats, références de stations et cohérence des incidents. L’import applique les règles de validation et enregistre les lignes rejetées dans `docs/journal-import.csv`.

## Choix écoresponsables

- Les listes sont paginées côté serveur, avec un maximum de 100 éléments. L’API ne renvoie que la page demandée.
- Le front ne se rafraîchit pas tout seul. Les indicateurs se mettent à jour quand l’utilisateur change les filtres ou clique sur le bouton « Actualiser ».
- La liste des communes est mise en cache pendant une heure grâce à `st.cache_data`. Cela évite de relire toutes les stations à chaque affichage.
- Les indicateurs sont agrégés en SQL dans PostgreSQL ; le front reçoit les résultats déjà calculés.

## Limites connues

- L’application est conçue pour un poste de démonstration local ; il n’y a pas de déploiement public ni de HTTPS configuré.
- Les données affichées viennent des trois CSV fournis. Elles ne se synchronisent pas automatiquement avec une source externe.
- Le front n’actualise les indicateurs que sur demande ou après une modification des filtres.