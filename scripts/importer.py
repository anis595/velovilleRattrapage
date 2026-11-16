"""Import et fiabilisation des trois exports CSV dans PostgreSQL.

À compléter : lire data/stations.csv, data/trajets.csv et data/incidents.csv,
appliquer les règles de fiabilisation (api/services/fiabilisation.py),
charger les lignes valides, journaliser les rejets et les avertissements.
Le script doit être idempotent : deux exécutions successives laissent la
base dans le même état.

Usage prévu : python scripts/importer.py [--dossier data]
"""

import csv
from sqlalchemy import text
from api.database import engine
from datetime import datetime
from api.services.fiabilisation import (
    valider_capacite,
    normaliser_identifiant_velo,
    normaliser_horodatage_trajet,
    valider_station,
    valider_duree,
    valider_usager,
    normalise_statut,
    convertir_horodatage_incident,
    valider_cible_incident,
    valider_dates_incident,
)


def lire_csv(chemin):
    lignes = []

    with open(chemin, mode="r", encoding="utf-8", newline="") as fichier:
        lecteur = csv.DictReader(fichier)
        for ligne in lecteur:
            lignes.append(ligne)
    return lignes


def ajouter_entree_journal(
    journal, fichier_source, identifiant, colonne, valeur, motif, decision
):
    entree = {
        "fichier_source": fichier_source,
        "identifiant": identifiant,
        "colonne": colonne,
        "valeur": valeur,
        "motif": motif,
        "decision": decision,
    }

    journal.append(entree)


def ecrire_journal(journal, chemin):
    colonnes = [
        "fichier_source",
        "identifiant",
        "colonne",
        "valeur",
        "motif",
        "decision",
    ]

    with open(chemin, mode="w", encoding="utf-8", newline="") as fichier:
        redacteur = csv.DictWriter(fichier, fieldnames=colonnes)
        redacteur.writeheader()
        redacteur.writerows(journal)


def preparer_station(ligne):
    station = {}

    station["station_id"] = ligne["station_id"]
    station["nom"] = ligne["nom"]
    station["commune"] = ligne["commune"]

    station["capacite"] = valider_capacite(ligne["capacite"])

    if ligne["latitude"] == "":
        station["latitude"] = None
    else:
        station["latitude"] = float(ligne["latitude"])

    if ligne["longitude"] == "":
        station["longitude"] = None
    else:
        station["longitude"] = float(ligne["longitude"])

    if ligne["date_mise_en_service"] == "":
        station["date_mise_en_service"] = None
    else:
        station["date_mise_en_service"] = datetime.strptime(
            ligne["date_mise_en_service"], "%Y-%m-%d"
        ).date()

    return station


def preparer_trajet(ligne, stations_connues):
    trajet = {}

    trajet["trajet_id"] = ligne["trajet_id"]

    trajet["velo_id"] = normaliser_identifiant_velo(ligne["velo_id"])

    trajet["depart_horodatage"] = normaliser_horodatage_trajet(
        ligne["depart_horodatage"]
    )

    trajet["station_depart"] = valider_station(
        ligne["station_depart"], stations_connues
    )

    trajet["station_arrivee"] = valider_station(
        ligne["station_arrivee"], stations_connues, obligatoire=False
    )

    trajet["duree_secondes"] = valider_duree(ligne["duree_secondes"])

    trajet["type_usager"] = ligne["type_usager"]

    trajet["usager_ref"] = valider_usager(ligne["type_usager"], ligne["usager_ref"])

    return trajet


def preparer_incident(ligne, stations_connues):
    incident = {}

    incident["incident_id"] = ligne["incident_id"]
    incident["type_incident"] = ligne["type_incident"]

    incident["statut"] = normalise_statut(ligne["statut"])

    if ligne["velo_id"] == "":
        incident["velo_id"] = None
    else:
        incident["velo_id"] = normaliser_identifiant_velo(ligne["velo_id"])

    if ligne["station_id"] == "":
        incident["station_id"] = None
    else:
        incident["station_id"] = ligne["station_id"]

    incident["cible"] = valider_cible_incident(
        ligne["cible"], incident["velo_id"], incident["station_id"], stations_connues
    )

    incident["date_signalement"] = convertir_horodatage_incident(
        ligne["date_signalement"]
    )

    date_resolution = convertir_horodatage_incident(ligne["date_resolution"])

    incident["date_resolution"] = valider_dates_incident(
        incident["statut"], incident["date_signalement"], date_resolution
    )

    if ligne["technicien"] == "":
        incident["technicien"] = None
    else:
        incident["technicien"] = ligne["technicien"]

    return incident


def inserer_station(connexion, station):
    requete = text("""
        INSERT INTO station (
            station_id, nom, commune, capacite,
            latitude, longitude, date_mise_en_service
        )
        VALUES (
            :station_id, :nom, :commune, :capacite,
            :latitude, :longitude, :date_mise_en_service
        )
        ON CONFLICT (station_id) DO NOTHING
    """)

    connexion.execute(requete, station)


def inserer_trajet(connexion, trajet):
    requete = text("""
        INSERT INTO trajet (
            trajet_id, velo_id, depart_horodatage,
            station_depart, station_arrivee,
            duree_secondes, type_usager, usager_ref
        )
        VALUES (
            :trajet_id, :velo_id, :depart_horodatage,
            :station_depart, :station_arrivee,
            :duree_secondes, :type_usager, :usager_ref
        )
        ON CONFLICT (trajet_id) DO NOTHING
    """)

    connexion.execute(requete, trajet)


def inserer_incident(connexion, incident):
    requete = text("""
        INSERT INTO incident (
            incident_id, date_signalement, cible,
            velo_id, station_id, type_incident,
            statut, date_resolution, technicien
        )
        VALUES (
            :incident_id, :date_signalement, :cible,
            :velo_id, :station_id, :type_incident,
            :statut, :date_resolution, :technicien
        )
        ON CONFLICT (incident_id) DO NOTHING
    """)

    connexion.execute(requete, incident)


def recuperer_stations_connues(connexion):
    requete = text("SELECT station_id FROM station")
    resultat = connexion.execute(requete)

    stations_connues = []

    for ligne in resultat:
        stations_connues.append(ligne[0])

    return stations_connues


def main() -> None:
    raise NotImplementedError("À compléter")


if __name__ == "__main__":
    main()
