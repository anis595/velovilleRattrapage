# Schéma de données

## Modèle logique de données

`PK` désigne une clé primaire, `FK` une clé étrangère et `NULL` une valeur facultative.

```text
station(station_id PK, nom, commune, capacite, latitude NULL,
        longitude NULL, date_mise_en_service NULL)
trajet(trajet_id PK, velo_id, depart_horodatage,
       station_depart FK -> station.station_id,
       station_arrivee FK -> station.station_id NULL,
       duree_secondes, type_usager, usager_ref NULL)
incident(incident_id PK, date_signalement, cible, velo_id NULL,
         station_id FK -> station.station_id NULL, type_incident,
         statut, date_resolution NULL, technicien NULL)
utilisateur(id_utilisateur PK, username UNIQUE, mot_de_passe_hash, role)
```

Une station peut être le départ ou l'arrivée de plusieurs trajets et être visée par plusieurs incidents. Un incident visant un vélo ne renseigne pas `station_id`. Le schéma exécutable se trouve dans `sql/schema.sql`.

## Tables et contraintes

| Table | Rôle et contraintes principales |
| --- | --- |
| `station` | `station_id` est unique et obligatoire. `nom` et `commune` sont obligatoires. `capacite` est un entier strictement positif. Les coordonnées et la date de mise en service sont facultatives. |
| `trajet` | `trajet_id` est unique. Le départ référence une station existante ; l'arrivée peut être absente, mais doit référencer une station si elle est présente. L'horodatage, la durée, le type d'usager et le vélo sont obligatoires. La durée est positive et le type d'usager vaut `abonne` ou `occasionnel`. |
| `incident` | `incident_id` est unique. La cible vaut `velo` ou `station` ; exactement la référence correspondante est renseignée. Une station visée doit exister. Le statut vaut `ouvert`, `en_cours` ou `resolu`. La date de résolution est présente seulement pour un incident résolu et ne précède pas le signalement. |
| `utilisateur` | Identifiant numérique en clé primaire, nom de connexion unique, hachage du mot de passe et rôle obligatoires. Le rôle vaut `exploitant` ou `direction`. |

## Règles de gestion RG1 à RG8

| Règle | Application dans la solution |
| --- | --- |
| RG1 | La clé primaire `station_id` garantit l'unicité ; `CHECK (capacite > 0)` et la validation de l'import imposent une capacité positive. |
| RG2 | `station_depart` est obligatoire et les deux références de station sont des clés étrangères. L'import vérifie leur présence dans le référentiel avant insertion. |
| RG3 | `station_arrivee` accepte `NULL`. L'import conserve ces trajets ; l'indicateur des stations actives ne compte une arrivée que si elle est renseignée. |
| RG4 | La colonne `duree_secondes` est entière avec `CHECK (duree_secondes > 0)` ; l'import rejette les durées invalides. |
| RG5 | `usager_ref` est facultatif dans le schéma. L'import impose un pseudonyme pour `abonne` et aucune référence pour `occasionnel`. Le schéma ne stocke pas d'identité directe. |
| RG6 | Une contrainte `CHECK` relie `cible` à `velo_id` ou `station_id`, de façon exclusive. La clé étrangère et l'import vérifient les stations visées. |
| RG7 | Une contrainte `CHECK` limite les statuts. L'import normalise leur écriture ; les transitions autorisées sont contrôlées par le service de modification des incidents. |
| RG8 | Une contrainte `CHECK` relie statut et date de résolution et vérifie l'ordre des dates. L'import rejette les dates incohérentes ; l'absence de technicien après prise en charge donne un avertissement sans rejet. |

Les contraintes SQL protègent la base lors d'une insertion directe. Les vérifications de format et les normalisations des CSV sont réalisées dans l'import avant l'insertion.

## Audit des données

J'ai vérifié les trois fichiers avec pandas, sans modifier les CSV.

### Stations

Je n'ai pas trouvé d'erreur dans les contrôles effectués.

### Trajets

| Problème trouvé                         | Nombre de lignes | Traitement prévu                                                          |
| --------------------------------------- | ---------------: | ------------------------------------------------------------------------- |
| Doublons exacts                         |       12 en trop | Garder une seule occurrence et noter les doublons écartés dans le journal |
| Durée nulle ou négative                 |               10 | Rejeter les lignes et noter le motif                                      |
| Station d'arrivée S999 inconnue         |                7 | Rejeter les lignes et noter le motif                                      |
| Date de départ dans un autre format     |                5 | Remettre au format attendu et noter la correction                         |
| Identifiant de vélo avec un v minuscule |                6 | Remplacer le v par V et noter la correction                               |

Il y a aussi 23 stations d'arrivée vides. C'est autorisé par RG3 :
ce n'est pas une raison pour rejeter ces lignes.

### Incidents

| Problème trouvé                         | Nombre de lignes | Traitement prévu                                                   |
| --------------------------------------- | ---------------: | ------------------------------------------------------------------ |
| Statuts écrits différemment             |              125 | Uniformiser en ouvert, en_cours ou resolu et noter la correction   |
| Résolution avant le signalement         |                3 | Rejeter les lignes et noter le motif                               |
| Technicien absent après prise en charge |               25 | Garder les lignes si le reste est valide et noter un avertissement |

Aucun doublon exact ni problème de cible n'a été trouvé dans les incidents.

### Attention aux comptages

Une ligne peut avoir plusieurs problèmes, donc je ne dois pas
additionner directement les nombres.

Par exemple, T480596 apparaît deux fois avec une durée négative.
Il est donc présent dans les contrôles des doublons et des durées.

Les traitements seront appliqués pendant l'import.
