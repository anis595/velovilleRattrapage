-- Schéma de la base veloville (PostgreSQL 14+).
-- À compléter en respectant le contrat du sujet (types, clés, contraintes).
-- Le script doit être rejouable : prévoir les DROP ... IF EXISTS ou
-- CREATE TABLE IF NOT EXISTS.

-- ---------------------------------------------------------------
-- 1. Table station
-- ---------------------------------------------------------------
 CREATE TABLE IF NOT EXISTS station(
    station_id VARCHAR(10) PRIMARY KEY,
    nom VARCHAR(60) NOT NULL,
    capacite INT NOT NULL CHECK (capacite > 0),
    latitude NUMERIC(8,5),
    longitude NUMERIC(8,5),
    date_mise_en_service DATE,
    commune VARCHAR(40) NOT NULL

 );

-- ---------------------------------------------------------------
-- 2. Table trajet
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trajet(
    trajet_id VARCHAR(12) PRIMARY KEY,
    station_depart VARCHAR(10) NOT NULL,
    station_arrivee VARCHAR(10),
    FOREIGN KEY (station_depart) REFERENCES station(station_id),
    FOREIGN KEY (station_arrivee) REFERENCES station(station_id),
    depart_horodatage TIMESTAMP NOT NULL,
    duree_secondes INT NOT NULL CHECK (duree_secondes > 0),
    type_usager VARCHAR(12) NOT NULL
    CHECK (type_usager IN ('abonne', 'occasionnel')),
    velo_id VARCHAR(8) NOT NULL,
    usager_ref VARCHAR(9)
);


-- ---------------------------------------------------------------
-- 3. Table incident
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incident (
    incident_id VARCHAR(12) PRIMARY KEY,
    date_signalement TIMESTAMP NOT NULL,
    velo_id VARCHAR(8),
    station_id VARCHAR(10),
    date_resolution TIMESTAMP,
    technicien VARCHAR(40),
    FOREIGN KEY (station_id) REFERENCES station(station_id),
    statut VARCHAR(8) NOT NULL,
    CHECK (statut IN (  
        'ouvert',
        'en_cours',
        'resolu')),
    cible VARCHAR(8) NOT NULL,
    CHECK (cible IN ('velo', 'station')),
    type_incident VARCHAR(30) NOT NULL
    CHECK (
    (cible = 'velo' AND velo_id IS NOT NULL AND station_id IS NULL)
    OR
    (cible = 'station' AND station_id IS NOT NULL AND velo_id IS NULL)
)
  CHECK ((
        statut = 'resolu'
        AND date_resolution IS NOT NULL
        AND date_resolution >= date_signalement)
    OR
    (
        statut IN ('en_cours', 'ouvert')
        AND date_resolution IS NULL
    )
)
);

-- ---------------------------------------------------------------
-- 4. Table utilisateur
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS utilisateur (
    id_utilisateur SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    mot_de_passe_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('exploitant', 'direction'))
);

-- ---------------------------------------------------------------
-- 5. Index utiles aux filtres et aux indicateurs
-- ---------------------------------------------------------------

