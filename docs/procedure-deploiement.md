# Procédure de déploiement

Cette procédure utilise PowerShell sur Windows et part d'un clone du dépôt. Exécuter les commandes depuis la racine du projet, sauf indication contraire.

## 1. Prérequis

Installer Python 3.12, PostgreSQL 14 ou plus récent (avec `psql`, `pg_dump` et `pg_restore`) et Git. Démarrer le service PostgreSQL. Vérifier que les commandes sont accessibles dans le terminal :

```powershell
py -3.12 --version
psql --version
pg_dump --version
```

## 2. Récupérer le projet et installer Python

```powershell
git clone https://github.com/anis595/velovilleRattrapage.git
Set-Location velovilleRattrapage
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Créer le rôle et la base

Ouvrir `psql -U postgres -d postgres` avec le mot de passe administrateur PostgreSQL, puis saisir :

```sql
CREATE ROLE veloville LOGIN;
\password veloville
CREATE DATABASE veloville OWNER veloville;
\q
```

La commande `\password` demande le nouveau mot de passe sans le placer en clair dans l'historique SQL. Si le rôle ou la base existe déjà, vérifier leur propriétaire et passer à l'étape suivante.

## 4. Configurer l'environnement et les tables

```powershell
Copy-Item .env.example .env
```

Dans `.env`, adapter `DATABASE_URL` avec le mot de passe choisi pour le rôle `veloville`, définir une valeur longue et personnelle pour `JWT_SECRET`, et vérifier `API_URL=http://localhost:8000`. Ne pas ajouter `.env` au dépôt. Si le mot de passe contient des caractères spéciaux réservés dans une URL, les encoder dans `DATABASE_URL`.

Créer les tables, puis les deux comptes de démonstration :

```powershell
psql -h localhost -U veloville -d veloville -v ON_ERROR_STOP=1 -f sql/schema.sql
psql -h localhost -U veloville -d veloville -v ON_ERROR_STOP=1 -f sql/comptes.sql
```

Le mot de passe de démonstration des comptes `exploitant01` et `direction01` est `Formation2026!`. Les hachages sont stockés dans la base.

## 5. Importer les CSV

```powershell
.\.venv\Scripts\python.exe scripts/importer.py
```

Le script charge les stations, les trajets, puis les incidents. Il affiche les nombres de lignes valides, rejetées et en doublon et écrit le journal dans `docs/journal-import.csv`. Une seconde exécution ne doit pas créer de doublons.

## 6. Démarrer et vérifier l'application

Dans un premier terminal :

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

Dans un second terminal, depuis la racine du projet :

```powershell
Invoke-RestMethod http://127.0.0.1:8000/sante
.\.venv\Scripts\python.exe -m streamlit run front/app.py
```

`GET /sante` doit renvoyer `{"statut":"ok"}`. L'API propose aussi `http://127.0.0.1:8000/docs`. Vérifier la connexion dans le front avec l'un des comptes de démonstration, puis l'affichage des stations, incidents et indicateurs.

## 7. Sauvegarder et restaurer

Créer une sauvegarde au format personnalisé PostgreSQL depuis la racine du projet. `pg_dump` demande le mot de passe du rôle :

```powershell
New-Item -ItemType Directory -Force sauvegardes | Out-Null
$horodatage = Get-Date -Format 'yyyyMMdd_HHmmss'
pg_dump -h localhost -U veloville -d veloville -Fc -f "sauvegardes/veloville_$horodatage.dump"
```

Vérifier le fichier avec `pg_restore --list sauvegardes/veloville_AAAAMMJJ_HHMMSS.dump` en remplaçant le nom par celui créé. Pour lancer la sauvegarde automatisée depuis un terminal Git Bash ou Linux, définir les variables PostgreSQL standard, puis lancer le script :

```bash
export PGHOST=localhost PGPORT=5432 PGUSER=veloville PGDATABASE=veloville
bash scripts/sauvegarde.sh
```

`pg_dump` demande le mot de passe si nécessaire. Le script utilise les variables du terminal, sans ajouter de paramètre de sauvegarde à `.env`. Il crée le même format de fichier et renvoie une erreur si `pg_dump` échoue.

Pour restaurer une sauvegarde dans une **base vide** dont `veloville` est propriétaire, après avoir arrêté l'API :

```powershell
pg_restore -h localhost -U veloville -d veloville --no-owner --no-privileges "sauvegardes/veloville_AAAAMMJJ_HHMMSS.dump"
```

Sur une base déjà remplie, la restauration créerait des objets en double : créer une autre base vide ou supprimer explicitement les objets après avoir conservé une sauvegarde. Relancer l'API et vérifier à nouveau `/sante`, puis la présence des données et la connexion des deux comptes.
