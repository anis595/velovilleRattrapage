"""Tests des fonctions de calcul des indicateurs.

À compléter : vérifier les agrégats sur un jeu de données connu.
"""
"""Tests des trois indicateurs sur un jeu de données connu."""

from datetime import date

import pytest

from api.database import engine
from api.services.indicateurs import (
    activite_par_jour,
    incidents_par_statut,
    stations_actives,
)


@pytest.fixture
def connexion_test():
    """Crée des tables temporaires et annule leur contenu après le test."""
    with engine.connect() as connexion:
        transaction = connexion.begin()
        try:
            connexion.exec_driver_sql("""
                CREATE TEMP TABLE station (
                    station_id TEXT, nom TEXT
                ) ON COMMIT DROP
            """)
            connexion.exec_driver_sql("""
                CREATE TEMP TABLE trajet (
                    trajet_id TEXT,
                    station_depart TEXT,
                    station_arrivee TEXT,
                    depart_horodatage TIMESTAMP
                ) ON COMMIT DROP
            """)
            connexion.exec_driver_sql("""
                CREATE TEMP TABLE incident (
                    statut TEXT,
                    date_signalement TIMESTAMP,
                    date_resolution TIMESTAMP
                ) ON COMMIT DROP
            """)

            connexion.exec_driver_sql("""
                INSERT INTO station VALUES
                ('S001', 'Station A'),
                ('S002', 'Station B'),
                ('S003', 'Station C')
            """)
            connexion.exec_driver_sql("""
                INSERT INTO trajet VALUES
                ('T1', 'S001', 'S002', '2026-08-24 08:00'),
                ('T2', 'S001', 'S002', '2026-08-24 09:00'),
                ('T3', 'S002', 'S001', '2026-08-25 10:00')
            """)
            connexion.exec_driver_sql("""
                INSERT INTO incident VALUES
                ('ouvert', '2026-08-24 08:00', NULL),
                ('resolu', '2026-08-24 08:00', '2026-08-24 10:00'),
                ('resolu', '2026-08-24 08:00', '2026-08-24 12:00')
            """)

            yield connexion
        finally:
            transaction.rollback()


def test_activite_par_jour(connexion_test):
    """Vérifie les comptes, l’ordre et les bornes incluses."""
    assert activite_par_jour(connexion_test) == [
        {"jour": "2026-08-24", "nb_trajets": 2},
        {"jour": "2026-08-25", "nb_trajets": 1},
    ]
    assert activite_par_jour(
        connexion_test, date(2026, 8, 24), date(2026, 8, 24)
    ) == [
        {"jour": "2026-08-24", "nb_trajets": 2},
    ]


def test_stations_actives(connexion_test):
    """Vérifie les mouvements et le départage par identifiant."""
    assert stations_actives(connexion_test, 2) == [
        {
            "station_id": "S001",
            "nom": "Station A",
            "nb_departs": 2,
            "nb_arrivees": 1,
        },
        {
            "station_id": "S002",
            "nom": "Station B",
            "nb_departs": 1,
            "nb_arrivees": 2,
        },
    ]


def test_incidents_par_statut(connexion_test):
    """Vérifie les effectifs et la moyenne des résolutions."""
    resultat = incidents_par_statut(connexion_test)

    assert resultat["donnees"] == [
        {"statut": "ouvert", "nb_incidents": 1},
        {"statut": "resolu", "nb_incidents": 2},
    ]
    assert resultat["delai_moyen_resolution_heures"] == 3.0

    connexion_test.exec_driver_sql(
        "DELETE FROM incident WHERE statut = 'resolu'"
    )
    assert incidents_par_statut(connexion_test)[
        "delai_moyen_resolution_heures"
    ] is None