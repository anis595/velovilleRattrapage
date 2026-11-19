# Matrice des rôles et des droits

Les codes indiquent la réponse attendue pour une requête valide. Un jeton absent, invalide ou expiré donne `401` sur les routes protégées. Un utilisateur connecté sans le rôle requis reçoit `403`.

| Route | Anonyme | Exploitant | Direction |
| --- | --- | --- | --- |
| `GET /sante` | `200` | `200` | `200` |
| `POST /auth/login` | `200` si identifiants valides, sinon `401` | `200` si identifiants valides, sinon `401` | `200` si identifiants valides, sinon `401` |
| `GET /stations` | `401` | `200` | `200` |
| `GET /stations/{station_id}` | `401` | `200` | `200` |
| `GET /trajets` | `401` | `200` | `200` |
| `GET /incidents` | `401` | `200` | `200` |
| `PUT /incidents/{incident_id}/statut` | `401` | `200` | `403` |
| `GET /indicateurs/activite-par-jour` | `401` | `200` | `200` |
| `GET /indicateurs/stations-actives` | `401` | `200` | `200` |
| `GET /indicateurs/incidents-par-statut` | `401` | `200` | `200` |

Une station ou un incident inexistant peut donner `404`. Une saisie invalide peut donner `422`. Ces réponses dépendent de la requête et ne modifient pas les droits ci-dessus.

## Données sensibles

| Donnée | Mesure prise |
| --- | --- |
| Mots de passe | La base conserve un hachage bcrypt. La connexion vérifie le mot de passe contre ce hachage ; l'API ne renvoie pas le mot de passe ni son hachage. |
| `usager_ref` pseudonymisé | La référence ne contient pas le nom de l'usager. Sa consultation passe par une route protégée par JWT. |
| Jeton JWT | Il est signé avec `JWT_SECRET`, possède une expiration et reste dans la session Streamlit. Le front l'envoie dans l'en-tête `Authorization`, ne l'affiche pas et le retire de la session à la déconnexion. |
| Paramètres de connexion et secret JWT | `DATABASE_URL` et `JWT_SECRET` sont lus dans l'environnement. Le fichier `.env` est ignoré par Git et `.env.example` ne contient pas de secret réel. |

Le front réserve la modification du statut d'un incident à l'exploitant et affiche en français un refus `403` renvoyé par l'API.
