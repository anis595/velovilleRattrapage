# Récapitulatif du travail sur VéloVille

Récapitulatif de notre conversation, préparé le 12 novembre 2026.

Ce document rassemble le travail réalisé, les résultats obtenus, les difficultés rencontrées et le point de reprise. Ce n'est pas une transcription mot à mot ni une validation finale du TP. Les résultats de PostgreSQL et les comptages viennent des sorties partagées pendant la conversation. Les fichiers du projet ont été relus au moment de rédiger ce récapitulatif, sans relancer l'import ou les tests.

## 1. Notre façon de travailler

Mon objectif est de refaire le TP moi-même et de comprendre ce que je fais.

- Rester dans les consignes du sujet, sans ajouter d'exercices ou de fonctionnalités.
- Rappeler la référence et l'énoncé exact pour chaque question abordée.
- S'appuyer sur mes cours autant que possible et signaler les compléments.
- Donner des exemples concrets, avec un vocabulaire simple.
- Me laisser écrire le code ; donner un indice ou du code quand je le demande.
- Travailler par blocs cohérents ou par fonctions complètes, sans valider chaque ligne séparément.
- Me laisser faire les commits et les push GitHub.

Le début a été trop découpé, surtout pendant l'audit. L'étape de configuration du fichier `.env` avait aussi été sautée dans l'accompagnement, puis reprise. Nous avons décidé d'être plus directs et de vérifier l'ordre des consignes.

## 2. Sujet et documents consultés

Le projet demandé est une application de valorisation des données de vélos en libre-service : stations, trajets et incidents.

Technologies imposées : Python, PostgreSQL, FastAPI et Streamlit. La V1 prévoit trois indicateurs, deux rôles applicatifs et quatre écrans. La restitution utilise des tableaux et des métriques, sans graphiques.

Les cinq travaux du sujet portent sur :

1. L'environnement, les données, les composants et les corrections.
2. L'API, le front, les tests, l'accessibilité et l'écoresponsabilité.
3. La recette et le suivi des anomalies.
4. L'authentification, les droits et les données sensibles.
5. La documentation, Git et la maintenance préventive.

Nous avons consulté le sujet, le cahier des charges de référence, le dictionnaire des données, les maquettes, le plan de recette, le README du squelette et les supports de cours.

Deux ambiguïtés ont été signalées :

- Le sujet présente la purge comme un bonus, alors que le cahier des charges prévoit un script de purge en V1.
- Les conditions générales de recette prévoient un import déjà exécuté, alors que REC-01 demande de partir sans import.

Ces points n'ont pas été tranchés par une consigne inventée.

## 3. Préparation du projet

**Référence : Travail 1 — Consigne 1 : « Initialisez le dépôt Git à partir du squelette fourni (voir `README-SQUELETTE.md`), créez un environnement virtuel, installez les dépendances et fixez leurs versions dans `requirements.txt`. »**

Le squelette fourni a été copié dans le dossier `veloville`, à la racine du projet. Je l'ai ouvert dans VS Code.

Nous avons ensuite :

- Initialisé le dépôt Git et réalisé le premier commit.
- Associé le dépôt GitHub `anis595/velovilleRattrapage`.
- Associé la branche locale `main` à `origin/main` lors du premier push.
- Créé et activé l'environnement virtuel `.venv`.
- Installé les dépendances et enregistré leurs versions dans `requirements.txt`.
- Copié `.env.example` en `.env`, puis renseigné la configuration locale.
- Généré une clé JWT et vérifié que `.env` ne figurait pas dans `git status`.

Une clé avait été partagée par erreur dans la conversation. Elle a été remplacée. Aucune clé ni valeur de mot de passe n'est recopiée dans ce document.

### Difficultés rencontrées

| Situation | Ce que nous avons compris |
|---|---|
| `cd veloville` échouait | Le terminal était déjà dans ce dossier ; la commande cherchait un sous-dossier supplémentaire. |
| `gir push` échouait | Il s'agissait d'une faute de frappe. |
| Premier `git push` refusé | Il fallait définir la branche distante suivie avec `git push -u origin main`. |
| `source .venv/bin/activate` échouait | Cette commande correspond à Linux/macOS ; PowerShell utilise `.\.venv\Scripts\Activate.ps1`. |
| `.env` restait invisible après modification | C'était attendu : Git ignore ce fichier. |

## 4. PostgreSQL et schéma SQL

**Référence : Travail 1 — Consigne 2 : « Créez la base `veloville` et le rôle PostgreSQL associé, puis écrivez `sql/schema.sql` conformément au contrat (types, clés primaires et étrangères, contraintes CHECK). Le script doit être rejouable. »**

PostgreSQL était déjà installé. Son outil `psql` a été trouvé dans `C:\Program Files\PostgreSQL\18\bin`.

Nous avons constaté que le rôle et la base `veloville` existaient déjà. Les commandes de vérification ont confirmé la connexion avec ce rôle et à cette base.

J'ai écrit les quatre tables dans `sql/schema.sql` :

- `station` : identifiant, nom, commune, capacité, coordonnées et date de mise en service.
- `trajet` : identifiant, vélo, départ, stations, durée, type d'usager et pseudonyme.
- `incident` : cible, références, dates, type, statut et technicien.
- `utilisateur` : identifiant, nom de connexion unique, mot de passe haché et rôle.

Nous avons travaillé sur les clés primaires, les clés étrangères, `NOT NULL` et les contraintes `CHECK`.

### Corrections apportées

- La durée doit être obligatoire en plus d'être strictement positive : ajout de `NOT NULL`.
- Un incident doit viser soit un vélo, soit une station, jamais les deux ni aucun.
- Un incident résolu doit avoir une date de résolution ; les autres ne doivent pas en avoir.
- La résolution ne doit pas précéder le signalement.

### Tables déjà existantes

La réexécution de `CREATE TABLE IF NOT EXISTS` n'applique pas les modifications à une table existante. Nous avons donc inspecté les tables avec les commandes `\dt` et `\d` de `psql`.

Les tables appartenaient à `postgres`. Une modification tentée avec `veloville` a été refusée. Nous avons utilisé le compte propriétaire pour ajouter :

- `NOT NULL` sur `trajet.duree_secondes`.
- La contrainte `incident_cible_coherence`.
- La contrainte `incident_resolution_coherence`.

Ces opérations ont réussi d'après les retours partagés. Cela ne remplace pas une vérification ultérieure de tout le schéma sur une base vierge.

## 5. Chargement des comptes

**Référence : Travail 1 — Consigne 3 : « Exécutez `sql/comptes.sql` pour charger les deux comptes fournis. »**

Le script fourni a été exécuté. PostgreSQL a répondu `INSERT 0 2` : deux lignes ont été insérées.

Nous avons distingué les comptes PostgreSQL, utilisés pour accéder à la base, des comptes applicatifs `exploitant01` et `direction01`, destinés à la connexion à VéloVille.

## 6. Audit des CSV

**Référence : Travail 1 — Consigne 4 : « Auditez les trois exports CSV avant de les charger. Ils proviennent du système de billettique et n'ont pas été fiabilisés : ils comportent des défauts de plusieurs natures. Appuyez-vous sur le dictionnaire des données, sur les règles de gestion RG1 à RG8 du cahier des charges et sur les contraintes du schéma pour les repérer. Votre audit (défauts identifiés, nombre de lignes concernées, traitement retenu) figure dans le README ou dans `docs/schema-donnees.md`. »**

J'ai créé `scripts/audit_donnees.py`, chargé les trois CSV avec pandas et travaillé sur les DataFrames `STATIONS`, `TRAJETS` et `INCIDENTS`. Les fichiers CSV sources n'ont pas été corrigés pendant l'audit.

### Stations : 120 lignes

| Contrôle réalisé | Résultat partagé |
|---|---|
| Capacités | 15, 20, 25, 30, 35 et 40 ; aucune valeur nulle ou négative observée |
| Identifiants | 120 valeurs distinctes ; format `S` suivi de trois chiffres respecté |
| Dates de mise en service | Aucune date absente ou non convertible avec le format indiqué |
| Communes | Neuf communes, sans variante visible dans le comptage |
| Latitude et longitude | Aucune valeur absente ou non convertible en nombre |
| Noms | Aucun nom manquant selon pandas ; longueur maximale de 43 caractères |
| Longueur des communes | Maximum de 17 caractères |

Répartition des communes : Lille 46, Roubaix 16, Tourcoing 14, Villeneuve d'Ascq 14, Marcq-en-Baroeul 8, Lambersart 6, Wattrelos 6, Croix 5, Mons-en-Baroeul 5.

Aucune anomalie n'a été trouvée dans ces contrôles. Cela ne signifie pas que chaque propriété possible des stations a été testée : par exemple, convertir une coordonnée en nombre ne valide pas sa position géographique.

### Trajets : 2 030 lignes

| Constat | Effectif | Traitement prévu |
|---|---:|---|
| Doublons exacts | 12 occurrences supplémentaires | Ne traiter qu'une occurrence et journaliser les doublons écartés |
| Durée nulle ou négative | 10 lignes | Rejet journalisé |
| Station d'arrivée `S999` inconnue | 7 lignes | Rejet journalisé |
| Départ au format jour/mois/année heure:minute | 5 lignes | Normalisation et avertissement |
| Identifiant de vélo commençant par `v` minuscule | 6 lignes | Normalisation en majuscule et avertissement |
| Station d'arrivée absente | 23 lignes | Absence autorisée par RG3 ; aucun rejet pour ce seul motif |

Les 10 lignes à durée invalide comprennent 7 durées négatives et 3 durées nulles, pour 9 identifiants distincts. Le trajet `T480596` apparaît deux fois à l'identique avec une durée de -120 secondes.

Les cinq départs à normaliser concernent `T480152`, `T480379`, `T481592`, `T481885` et `T481958`.

Les six identifiants de vélo à normaliser sont `v1281`, `v0685`, `v0800`, `v0959`, `v1788` et `v0936`.

Autres résultats partagés :

- Les répétitions de `trajet_id` sont entièrement expliquées par les doublons exacts.
- Aucune durée absente, non convertible en nombre ou non entière.
- Les 2 030 stations de départ appartiennent au référentiel.
- Les 2 030 identifiants de trajet respectent le format attendu.
- 1 232 trajets d'abonnés et 798 trajets occasionnels.
- Aucun abonné sans pseudonyme, aucun occasionnel avec pseudonyme.
- Les 1 232 pseudonymes renseignés respectent le format attendu.

Attention : les 798 références absentes des occasionnels ont d'abord été comptées comme des formats invalides avec `na=False`. Le contrôle a été repris sur les seules références renseignées : ce n'étaient pas 798 anomalies.

### Incidents : 180 lignes

| Constat | Effectif | Traitement prévu |
|---|---:|---|
| Statuts à normaliser | 125 lignes | Normalisation et avertissement |
| Résolution antérieure au signalement | 3 lignes | Rejet journalisé |
| Technicien absent après prise en charge | 25 lignes | Avertissement ; pas de rejet pour ce seul motif |

Détail des statuts à normaliser :

- `Ouvert` : 29 lignes, à convertir en `ouvert`.
- `en cours` et `En cours` : 46 lignes, à convertir en `en_cours`.
- `RESOLU` et `Resolu` : 50 lignes, à convertir en `resolu`.

Les dates incohérentes concernent `I2026-0028`, `I2026-0124` et `I2026-0178`.

Autres résultats partagés :

- Aucun doublon exact.
- 115 cibles vélo et 65 cibles station.
- Toutes les stations visées appartiennent au référentiel.
- Aucun incident ne renseigne des références incompatibles avec sa cible.
- Aucun signalement absent ou non convertible.
- Aucune résolution renseignée mais non convertible.
- Aucun incident résolu sans date de résolution.
- Aucun incident non résolu avec une date de résolution, après harmonisation temporaire des statuts pour le contrôle.

### Ne pas additionner directement les défauts

Une ligne peut apparaître dans plusieurs contrôles :

- `T480596` est à la fois dupliqué et porteur d'une durée négative.
- `T480152` a une date normalisable, mais reste à rejeter pour sa station d'arrivée `S999`.
- `I2026-0028` a un statut à normaliser et des dates incohérentes.

Les volumes définitifs importés, rejetés et écartés comme doublons n'ont pas encore été mesurés par un import.

### Trace écrite

Une section « Audit des données » a été ajoutée dans `docs/schema-donnees.md`. Le sujet autorise cet emplacement même si le fichier sert aussi à décrire le schéma. La partie MLD et description des tables reste à compléter.

## 7. Notions pandas travaillées

- Lire un CSV et sélectionner une colonne.
- Compter les valeurs avec `value_counts` et inclure les absences avec `dropna=False`.
- Repérer les doublons exacts ou ceux d'une seule colonne.
- Convertir des nombres et des dates avec `errors="coerce"`.
- Distinguer une valeur absente d'une valeur invalide.
- Utiliser `isna`, `notna`, `isin` et les contrôles de format de texte.
- Combiner des conditions avec `&`, `|` et `~`.
- Distinguer un filtre booléen, son comptage et l'affichage des lignes sélectionnées.

Exemple de difficulté résolue : appliquer `.sum()` au tableau filtré additionne les nombres et peut concaténer les textes ; cela n'affiche pas les lignes. Pour compter les lignes concernées, on somme le filtre booléen. Pour les afficher, on utilise ce filtre entre les crochets du DataFrame.

Ces méthodes ont servi à l'audit demandé. Elles n'ont pas toutes été vérifiées comme présentes dans les cours : il ne faut pas les présenter comme des extraits des supports.

## 8. Fonctions de fiabilisation écrites

**Référence : Travail 1 — Consigne 5 : « Écrivez les règles de fiabilisation sous forme de fonctions pures dans `api/services/fiabilisation.py` (une fonction par règle, sans accès à la base). »**

Nous avons commencé les fonctions dans `api/services/fiabilisation.py`.

Une fonction pure reçoit des valeurs et retourne un résultat ou signale une erreur, sans modifier la base, les fichiers ou une variable extérieure. L'importeur sera responsable des écritures et du journal.

| Fonction présente | Rôle et comportement actuel |
|---|---|
| `normaliser_identifiant_velo` | Retourne le texte en majuscules. Exemple : `v1281` devient `V1281`. Ne valide pas à elle seule le format. |
| `normalise_statut` | Reconnaît les variantes observées, retourne un des trois statuts attendus et lève une `ValueError` pour un statut inconnu. |
| `valider_duree` | Convertit une durée reçue comme texte en entier, refuse zéro et les valeurs négatives, retourne l'entier valide. |
| `normaliser_horodatage_trajet` | Essaie le format attendu, puis le format français observé. Retourne un objet `datetime`. |
| `valider_station` | Refuse une référence obligatoire absente ou une station inconnue. Retourne `None` pour une absence facultative et la référence lorsqu'elle est valide. |

### Notions comprises pendant l'écriture

- Chaque comparaison autour de `or` doit être écrite complètement : une chaîne non vide utilisée seule est considérée comme vraie.
- Les valeurs déjà conformes doivent aussi être acceptées par la normalisation.
- `return` transmet le résultat à l'appelant ; sans retour explicite, une fonction terminée normalement renvoie `None`.
- `raise ValueError` signale un refus ; ce n'est pas une panne inattendue quand on teste volontairement une entrée invalide.
- Un `try` permet d'essayer une conversion ; `except ValueError` permet d'essayer le second format.
- L'indentation décide si le contrôle du caractère obligatoire est effectué seulement quand la référence est absente.
- Une référence facultative peut être vide, mais si elle est renseignée, elle doit quand même être valide.

### Vérifications manuelles

Des appels temporaires avec `print` ont servi à vérifier :

- Les identifiants de vélo minuscules et déjà conformes.
- Les variantes de statuts et le refus de `annule`.
- La conversion des durées et le refus des valeurs non positives.
- Les deux formats d'horodatage, qui doivent représenter le même instant.
- Une station connue et une référence facultative vide, affichant `S001` puis `None`.

Ce ne sont pas encore des tests automatisés pytest. Le fichier `tests/unit/test_fiabilisation.py` contient toujours son texte de squelette au moment de la relecture.

### Appui sur les cours

Dans `python_base.pdf`, nous avons vérifié :

- Page 16 : appel d'une fonction et paramètres.
- Page 17 : méthode de chaîne et exemple avec `.upper()`.
- Pages 54–55 : fonctions, paramètres, `def` et `return`.
- Page 56 : variables locales et globales.

Le cours de programmation orientée objet contient une partie sur les exceptions. `datetime.strptime` a été présenté comme un complément expliqué, pas comme une méthode dont la présence avait été vérifiée dans les supports.

### Point constaté lors de la relecture du 12 novembre

Les cinq fonctions sont enregistrées. La plupart des appels temporaires sont commentés, mais les deux `print` de vérification de `valider_station`, ainsi que la liste d'exemple `stations`, sont encore actifs en bas du fichier. Leur retrait avait été conseillé, mais n'est pas effectué dans le fichier relu. Ce récapitulatif ne les modifie pas.

## 9. Git et sauvegarde du travail

J'ai effectué les commits et les push moi-même. L'assistant a seulement inspecté le dépôt lorsqu'un push avait été évoqué, avant que je précise que je souhaitais le faire ; il n'a alors créé aucun commit ni poussé de modification.

Historique local observé lors de la préparation de ce récapitulatif :

| Commit | Message |
|---|---|
| `40cc550` | Initialiser le projet VéloVille depuis le squelette fourni |
| `ca02e2b` | Définir le schéma SQL et commencer l'audit des données |
| `d741f2c` | Documenter l'audit et ajouter les premières fonctions de fiabilisation |

Avant la création de ce document, le répertoire de travail était propre et Git indiquait `main...origin/main`, sans avance ni retard par rapport à sa référence distante locale. Aucun nouveau contact réseau n'a été fait pour revérifier GitHub.

Commandes utilisées : `git status`, `git diff`, `git add` avec les fichiers explicitement nommés, `git diff --cached --stat`, `git commit`, puis `git push`.

Nous avons aussi vu que :

- `q` permet de quitter l'affichage paginé de `git diff`.
- Les avertissements LF/CRLF concernent les fins de ligne et n'ont pas bloqué le commit.
- `.env`, `.venv` et les sauvegardes ne doivent pas être ajoutés au dépôt.

## 10. Incident de sélection à la souris

La sélection de texte disparaissait au relâchement de la souris dans la conversation et dans VS Code. Une sélection avec Maj et les flèches restait affichée. Cela orientait vers la souris ou le pavé tactile, sans diagnostic définitif. Le contournement proposé était la sélection au clavier puis Ctrl+C.

## 11. Où nous en sommes et quoi reprendre

Nous sommes dans le **Travail 1, consigne 5**. La fiabilisation est commencée, pas terminée.

Le script `scripts/importer.py` reste un squelette avec `NotImplementedError`. L'import des CSV, son journal, son idempotence et les volumes finaux n'ont pas encore été validés.

### Point de reprise convenu

Reprendre les fonctions de fiabilisation liées à la cohérence des incidents : cible, dates de résolution et traitement de l'absence du technicien selon les règles du sujet. Vérifier ensuite la couverture des règles nécessaires à l'import et préparer les tests unitaires demandés, sans ajouter de règles étrangères au TP.

Les fonctions existantes ne couvrent pas encore à elles seules toutes les validations du schéma et des règles RG1 à RG8. Un contrôle d'audit sans anomalie ne dispense pas d'implémenter la règle demandée dans la solution.

### Travail restant à l'échelle du TP

- Terminer les règles de fiabilisation et leurs tests.
- Réaliser l'import et le journal des rejets et avertissements, puis vérifier l'idempotence.
- Implémenter les trois indicateurs.
- Réaliser l'API, l'authentification et les contrôles de rôle.
- Réaliser les quatre écrans Streamlit.
- Compléter les tests et mesurer la couverture minimale de 60 % des modules métier.
- Dérouler les dix cas de recette, consigner les résultats et traiter les anomalies.
- Compléter la documentation, le MLD, la matrice des droits et la procédure de déploiement.
- Réaliser la sauvegarde et documenter la restauration.
- Préparer l'historique de versions, la branche fusionnée, les tags et le support de soutenance demandés.

Une estimation de 10 à 15 % du TP avait été donnée pendant la conversation. C'était une appréciation approximative à ce moment-là, pas une mesure d'avancement ni une note.

Ce nouveau récapitulatif n'est ni commité ni poussé automatiquement.
