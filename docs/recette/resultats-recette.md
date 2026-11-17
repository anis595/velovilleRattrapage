# Résultats de recette

| Cas | Résultat obtenu et preuve | Statut |
|---|---|---|
| REC-01 | Deux exécutions de `python scripts/importer.py` terminées sans erreur. Après chacune, `SELECT count(*)` donne 120 stations, 2002 trajets et 177 incidents, identiques aux comptages avant le test. Bilans affichés : stations 120/0/0, trajets 2002/16/12, incidents 177/3/0 (valides/rejets/doublons). La base était déjà importée avant ce passage. | OK |
| REC-02 | CSV : 120 stations, 2030 trajets, 180 incidents. Journal : 0 rejet station, 16 rejets trajet, 3 rejets incident, mais aucun doublon exact journalisé. Pour les trajets, 2002 + 16 + 0 = 2018, soit 12 lignes de moins que le CSV ; le bilan de l'importeur compte pourtant 12 doublons. Les six colonnes requises sont présentes. La requête de cohérence des stations d'arrivée renvoie 0. | KO |
| REC-03 | Connexions de `exploitant01` et `direction01` vérifiées dans Swagger pendant la séance : jeton reçu pour chaque compte, type `bearer`, rôles respectifs `exploitant` et `direction`. Le jeton direction a permis d'atteindre le contrôle de rôle du PUT (réponse 403). Jetons non consignés. | OK |
| REC-04 | Deux essais de `POST /auth/login` dans Swagger : `exploitant01` avec un mauvais mot de passe, puis un identifiant inconnu avec le mot de passe de démonstration. L'utilisateur a relevé 401 dans les deux cas. La route renvoie le même détail `Identifiants invalides` pour les deux chemins de refus. | OK |
| REC-05 | Dans Swagger, `GET /stations` sans jeton : 401 ; avec `jeton.invalide.xyz` : 401 ; `GET /sante` : 200 avec `{"statut":"ok"}`. Résultats confirmés par l'utilisateur. | OK |
| REC-06 | Sur `I2026-0002` initialement `ouvert`, PUT `en_cours` avec le rôle direction : 403 ; avec le rôle exploitant : 200 et statut `en_cours` ; répétition : 422. Trois codes confirmés par l'utilisateur. Lecture SQL finale : `I2026-0002`, `en_cours`. | OK |
| REC-07 | Avec le rôle direction dans Swagger : page 1 de 50, `total` 120, 50 résultats, premier `S001` ; page 3 de 50, 20 résultats ; filtre `Lille` avec taille 100, `total` 46 et communes conformes. Résultats confirmés par l'utilisateur. Requêtes locales via `TestClient` : `page=0` → 422 et `taille_page=101` → 422. | OK |
| REC-08 | Dans Swagger avec le rôle direction : `GET /stations/S001` → 200, identifiant `S001`, nom `Lille - Gare` ; `GET /stations/S999` → 404, détail `Station introuvable`. Résultats confirmés par l'utilisateur. | OK |
| REC-09 | `GET /indicateurs/activite-par-jour?date_debut=2026-08-24&date_fin=2026-08-30` → 200. Comparaison ligne à ligne avec le regroupement SQL du plan : identique pour 7 jours. Somme des trajets = 2002, égale au `total` de `GET /trajets` sur la même période (2002). | OK |
| REC-10 | Page Stations sans jeton : `Veuillez vous connecter.`, puis trace `StreamlitPageNotFoundError` sur `st.page_link("front/app.py", ...)`. Avec le rôle direction, page 99 : `Aucun résultat pour ces critères.`, sans trace ; total 120. API arrêtée : Stations et Indicateurs affichent le message français d'indisponibilité sans trace. API redémarrée : tableau Stations de nouveau affiché. La description du fichier est visible au-dessus du titre. | KO |

Première passe : 10 cas exécutés, 8 OK, 2 KO, 0 NT. Anomalies relevées avant correction : REC-02 (doublons absents du journal), REC-10 (trace sans jeton, description technique affichée).

Rejeu après correction d'ANO-001 : REC-02 OK le 17/11/2026. L'import affiche 2002 trajets valides, 16 rejets et 12 doublons ; le journal contient désormais 16 rejets invalides et 12 doublons exacts. Trois tests de non-régression passent dans `tests/unit/test_importer.py`.

Rejeu ciblé après correction d'ANO-002 : la déconnexion et les liens « Page de connexion » des pages Stations, Incidents et Indicateurs fonctionnent sans trace, confirmation utilisateur le 17/11/2026. REC-10 reste KO tant que l'affichage des descriptions techniques (ANO-003) n'est pas corrigé.
