# Schéma de données

À compléter : MLD textuel ou image, description des tables, clés et contraintes,
règles de gestion portées par le schéma.

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
