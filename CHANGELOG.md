# Journal des versions

## [0.2.1] - 2026-11-18

### Ajouté
- Documentation des rôles et droits, du schéma de données et du déploiement.
- Résultats de recette et fiches des trois anomalies relevées.

### Modifié
- README complété avec les commandes de lancement, les tests et l'audit.

### Corrigé
- ANO-001 : les 12 doublons exacts de trajets figurent dans le journal d'import.
- ANO-002 : les liens de retour à la connexion et la déconnexion fonctionnent depuis les pages Streamlit.
- ANO-003 : les descriptions techniques des scripts ne s'affichent plus dans les pages Streamlit.
- Rejeu de la recette : 10 cas OK sur 10 après corrections.

## [0.2.0] - 2026-11-17 (avant recette)

### Ajouté
- Import idempotent des stations, trajets et incidents avec validation et journal des rejets.
- API FastAPI : authentification JWT, routes protégées, consultation des ressources et trois indicateurs.
- Front Streamlit : connexion, stations, incidents et indicateurs.
- Tests unitaires et d'intégration ; 102 tests réussis et 78 % de couverture des services lors du contrôle.

### Modifié
- Schéma PostgreSQL et dépendances Python adaptés à la solution.

### Corrigé
- Formats de dates, identifiants de vélo et statuts normalisés lors de l'import ; lignes invalides rejetées.

## [0.1.0] - 2026-10-07

### Ajouté
- Initialisation du projet à partir du squelette fourni.
