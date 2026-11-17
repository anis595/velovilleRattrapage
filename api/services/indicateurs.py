"""Calcul des trois indicateurs VéloVille."""

from sqlalchemy import text


def activite_par_jour(session, date_debut=None, date_fin=None):
    """Compte les trajets par jour sur la période demandée."""
    requete = text("""
        SELECT
            CAST(depart_horodatage AS DATE) AS jour,
            COUNT(*) AS nb_trajets
        FROM trajet
        WHERE (CAST(:date_debut AS DATE) IS NULL
            OR CAST(depart_horodatage AS DATE) >= CAST(:date_debut AS DATE))
        AND (CAST(:date_fin AS DATE) IS NULL
               OR CAST(depart_horodatage AS DATE) <= CAST(:date_fin AS DATE))
        GROUP BY CAST(depart_horodatage AS DATE)
        ORDER BY jour ASC
    """)

    lignes = session.execute(
        requete,
        {"date_debut": date_debut, "date_fin": date_fin},
    )

    return [
        {"jour": ligne.jour.isoformat(), "nb_trajets": ligne.nb_trajets}
        for ligne in lignes
    ]

def stations_actives(session, limite=10):
    """Classe les stations selon leur nombre total de mouvements."""
    requete = text("""
        WITH mouvements AS (
            SELECT station_depart AS station_id, 1 AS depart, 0 AS arrivee
            FROM trajet
            UNION ALL
            SELECT station_arrivee AS station_id, 0 AS depart, 1 AS arrivee
            FROM trajet
            WHERE station_arrivee IS NOT NULL
        )
        SELECT
            station.station_id,
            station.nom,
            SUM(mouvements.depart) AS nb_departs,
            SUM(mouvements.arrivee) AS nb_arrivees
        FROM station
        JOIN mouvements ON mouvements.station_id = station.station_id
        GROUP BY station.station_id, station.nom
        ORDER BY
            SUM(mouvements.depart) + SUM(mouvements.arrivee) DESC,
            station.station_id ASC
        LIMIT :limite
    """)

    lignes = session.execute(requete, {"limite": limite})

    return [
        {
            "station_id": ligne.station_id,
            "nom": ligne.nom,
            "nb_departs": ligne.nb_departs,
            "nb_arrivees": ligne.nb_arrivees,
        }
        for ligne in lignes
    ]

def incidents_par_statut(session):
    """Compte les incidents par statut et calcule leur délai moyen de résolution."""
    requete_statuts = text("""
        SELECT statut, COUNT(*) AS nb_incidents
        FROM incident
        GROUP BY statut
        ORDER BY statut
    """)
    lignes = session.execute(requete_statuts)

    donnees = [
        {"statut": ligne.statut, "nb_incidents": ligne.nb_incidents}
        for ligne in lignes
    ]

    requete_delai = text("""
        SELECT ROUND(
            AVG(
                EXTRACT(EPOCH FROM (date_resolution - date_signalement))
                / 3600
            )::numeric,
            1
        ) AS delai_moyen
        FROM incident
        WHERE statut = 'resolu'
          AND date_resolution IS NOT NULL
    """)
    delai_moyen = session.execute(requete_delai).scalar_one()

    return {
        "donnees": donnees,
        "delai_moyen_resolution_heures": (
            float(delai_moyen) if delai_moyen is not None else None
        ),
    }
