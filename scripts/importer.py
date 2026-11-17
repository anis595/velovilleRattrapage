"""Import et fiabilisation des trois exports CSV dans PostgreSQL.

À compléter : lire data/stations.csv, data/trajets.csv et data/incidents.csv,
appliquer les règles de fiabilisation (api/services/fiabilisation.py),
charger les lignes valides, journaliser les rejets et les avertissements.
Le script doit être idempotent : deux exécutions successives laissent la
base dans le même état.

Usage prévu : python scripts/importer.py [--dossier data]
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

RACINE_PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE_PROJET))
from api.database import engine
from api.services.fiabilisation import (
    convertir_horodatage_incident,
    est_doublon_exact,
    normalise_statut,
    normaliser_horodatage_trajet,
    normaliser_identifiant_velo,
    valider_capacite,
    valider_cible_incident,
    valider_dates_incident,
    valider_duree,
    valider_identifiant_unique,
    valider_station,
    valider_usager,
    avertissement_technicien
)


class ErreurPreparation(ValueError):
    def __init__(self, colonne, motif):
        super().__init__(motif)
        self.colonne = colonne


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

    try:
        station["capacite"] = valider_capacite(ligne["capacite"])
    except ValueError as erreur:
        raise ErreurPreparation("capacite", str(erreur))

    try:
        if ligne["latitude"] == "":
            station["latitude"] = None
        else:
            station["latitude"] = float(ligne["latitude"])
    except ValueError as erreur:
        raise ErreurPreparation("latitude", str(erreur))

    try:
        if ligne["longitude"] == "":
            station["longitude"] = None
        else:
            station["longitude"] = float(ligne["longitude"])
    except ValueError as erreur:
        raise ErreurPreparation("longitude", str(erreur))

    try:
        if ligne["date_mise_en_service"] == "":
            station["date_mise_en_service"] = None
        else:
            station["date_mise_en_service"] = datetime.strptime(
                ligne["date_mise_en_service"], "%Y-%m-%d"
            ).date()
    except ValueError as erreur:
        raise ErreurPreparation("date_mise_en_service", str(erreur))

    return station


def preparer_trajet(ligne, stations_connues):
    trajet = {}

    trajet["trajet_id"] = ligne["trajet_id"]

    trajet["velo_id"] = normaliser_identifiant_velo(ligne["velo_id"])

    try:
        trajet["depart_horodatage"] = normaliser_horodatage_trajet(
            ligne["depart_horodatage"]
        )
    except ValueError as erreur:
        raise ErreurPreparation("depart_horodatage", str(erreur))

    try:
        trajet["station_depart"] = valider_station(
            ligne["station_depart"], stations_connues
        )
    except ValueError as erreur:
        raise ErreurPreparation("station_depart", str(erreur))

    try:
        trajet["station_arrivee"] = valider_station(
            ligne["station_arrivee"], stations_connues, obligatoire=False
        )
    except ValueError as erreur:
        raise ErreurPreparation("station_arrivee", str(erreur))

    try:
        trajet["duree_secondes"] = valider_duree(ligne["duree_secondes"])
    except ValueError as erreur:
        raise ErreurPreparation("duree_secondes", str(erreur))

    trajet["type_usager"] = ligne["type_usager"]

    # valider_usager vérifie deux colonnes :
    # identifier celle qui explique un éventuel rejet.
    if ligne["type_usager"] not in ("abonne", "occasionnel"):
        colonne_usager = "type_usager"
    else:
        colonne_usager = "usager_ref"

    try:
        trajet["usager_ref"] = valider_usager(ligne["type_usager"], ligne["usager_ref"])
    except ValueError as erreur:
        raise ErreurPreparation(colonne_usager, str(erreur))

    return trajet


def preparer_incident(ligne, stations_connues):
    incident = {}

    incident["incident_id"] = ligne["incident_id"]
    incident["type_incident"] = ligne["type_incident"]

    try:
        incident["statut"] = normalise_statut(ligne["statut"])
    except ValueError as erreur:
        raise ErreurPreparation("statut", str(erreur)) from erreur

    if ligne["velo_id"] == "":
        incident["velo_id"] = None
    else:
        incident["velo_id"] = normaliser_identifiant_velo(ligne["velo_id"])

    if ligne["station_id"] == "":
        incident["station_id"] = None
    else:
        incident["station_id"] = ligne["station_id"]

    try:
        incident["cible"] = valider_cible_incident(
            ligne["cible"],
            incident["velo_id"],
            incident["station_id"],
            stations_connues,
        )
    except ValueError as erreur:
        motif = str(erreur)

        if motif == "Identifiant vélo obligatoire":
            colonne = "velo_id"
        elif motif == "Une cible vélo ne doit pas avoir de station":
            colonne = "station_id"
        elif motif in (
            "Une cible station ne doit pas avoir de vélo",
        ):
            colonne = "velo_id"
        elif motif in ("Station obligatoire absente", "Station inconnue"):
            colonne = "station_id"
        else:
            colonne = "cible"

        raise ErreurPreparation(colonne, motif) from erreur

    try:
        incident["date_signalement"] = convertir_horodatage_incident(
            ligne["date_signalement"]
        )
    except ValueError as erreur:
        raise ErreurPreparation(
            "date_signalement", str(erreur)
        ) from erreur

    try:
        date_resolution = convertir_horodatage_incident(
            ligne["date_resolution"]
        )
    except ValueError as erreur:
        raise ErreurPreparation(
            "date_resolution", str(erreur)
        ) from erreur

    try:
        incident["date_resolution"] = valider_dates_incident(
            incident["statut"],
            incident["date_signalement"],
            date_resolution,
        )
    except ValueError as erreur:
        motif = str(erreur)

        if motif == "Date de signalement obligatoire":
            colonne = "date_signalement"
        else:
            colonne = "date_resolution"

        raise ErreurPreparation(colonne, motif) from erreur

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


def importer_stations(connexion, lignes, journal):
    lignes_deja_vues = []
    identifiants_deja_vus = []
    nb_valides = 0
    nb_rejets = 0
    nb_doublons = 0

    for ligne in lignes:
        if est_doublon_exact(ligne, lignes_deja_vues):
            ajouter_entree_journal(
                journal, "stations.csv", ligne["station_id"],
                "station_id", ligne["station_id"],
                "Doublon exact écarté", "rejet",
            )
            nb_doublons += 1
            continue

        identifiant = ligne["station_id"]
        lignes_deja_vues.append(ligne)

        try:
            valider_identifiant_unique(identifiant, identifiants_deja_vus)

        except ValueError as erreur:
            ajouter_entree_journal(
                journal,
                "stations.csv",
                identifiant,
                "station_id",
                identifiant,
                str(erreur),
                "rejet",
            )
            nb_rejets += 1
            continue
        identifiants_deja_vus.append(identifiant)

        try:
            station = preparer_station(ligne)

        except ErreurPreparation as erreur:
            ajouter_entree_journal(
                journal,
                "stations.csv",
                identifiant,
                erreur.colonne,
                ligne[erreur.colonne],
                str(erreur),
                "rejet",
            )
            nb_rejets += 1
            continue
        inserer_station(connexion, station)
        nb_valides += 1
    return {"valides": nb_valides, "rejets": nb_rejets, "doublons": nb_doublons}



def importer_trajets(connexion, lignes, stations_connues, journal):
    lignes_deja_vues = []
    identifiants_deja_vus = []
    nb_valides = 0
    nb_rejets = 0
    nb_doublons = 0

    for ligne in lignes:
        if est_doublon_exact(ligne, lignes_deja_vues):
            ajouter_entree_journal(
                journal, "trajets.csv", ligne["trajet_id"],
                "trajet_id", ligne["trajet_id"],
                "Doublon exact écarté", "rejet",
            )
            nb_doublons += 1
            continue

        identifiant = ligne["trajet_id"]
        lignes_deja_vues.append(ligne)

        try:
            valider_identifiant_unique(identifiant, identifiants_deja_vus)
        except ValueError as erreur:
            ajouter_entree_journal(
                journal,
                "trajets.csv",
                identifiant,
                "trajet_id",
                identifiant,
                str(erreur),
                "rejet",
            )
            nb_rejets += 1
            continue

        identifiants_deja_vus.append(identifiant)

        try:
            trajet = preparer_trajet(ligne, stations_connues)
        except ErreurPreparation as erreur:
            ajouter_entree_journal(
                journal,
                "trajets.csv",
                identifiant,
                erreur.colonne,
                ligne[erreur.colonne],
                str(erreur),
                "rejet",
            )
            nb_rejets += 1
            continue

        inserer_trajet(connexion, trajet)

        if ligne["velo_id"] != trajet["velo_id"]:
            ajouter_entree_journal(
                journal,
                "trajets.csv",
                identifiant,
                "velo_id",
                ligne["velo_id"],
                "Identifiant du vélo normalisé en majuscules",
                "normalisation",
            )

        horodatage_normalise = trajet["depart_horodatage"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        if ligne["depart_horodatage"] != horodatage_normalise:
            ajouter_entree_journal(
                journal,
                "trajets.csv",
                identifiant,
                "depart_horodatage",
                ligne["depart_horodatage"],
                "Horodatage normalisé",
                "normalisation",
            )

        nb_valides += 1

    return {
        "valides": nb_valides,
        "rejets": nb_rejets,
        "doublons": nb_doublons,
    }

def importer_incidents(connexion, lignes, stations_connues, journal):
    lignes_deja_vues = []
    identifiants_deja_vus = []
    nb_valides = 0
    nb_rejets = 0
    nb_doublons = 0

    for ligne in lignes:
        if est_doublon_exact(ligne, lignes_deja_vues):
            ajouter_entree_journal(
                journal, "incidents.csv", ligne["incident_id"],
                "incident_id", ligne["incident_id"],
                "Doublon exact écarté", "rejet",
            )
            nb_doublons += 1
            continue

        identifiant = ligne["incident_id"]
        lignes_deja_vues.append(ligne)

        try:
            valider_identifiant_unique(identifiant, identifiants_deja_vus)
        except ValueError as erreur:
            ajouter_entree_journal(
                journal, "incidents.csv", identifiant,
                "incident_id", identifiant, str(erreur), "rejet",
            )
            nb_rejets += 1
            continue

        identifiants_deja_vus.append(identifiant)

        try:
            incident = preparer_incident(ligne, stations_connues)
        except ErreurPreparation as erreur:
            ajouter_entree_journal(
                journal, "incidents.csv", identifiant,
                erreur.colonne, ligne[erreur.colonne],
                str(erreur), "rejet",
            )
            nb_rejets += 1
            continue

        inserer_incident(connexion, incident)

        if ligne["statut"] != incident["statut"]:
            ajouter_entree_journal(
                journal, "incidents.csv", identifiant,
                "statut", ligne["statut"],
                "Statut normalisé", "normalisation",
            )

        if incident["velo_id"] is not None and ligne["velo_id"] != incident["velo_id"]:
            ajouter_entree_journal(
                journal, "incidents.csv", identifiant,
                "velo_id", ligne["velo_id"],
                "Identifiant du vélo normalisé en majuscules",
                "normalisation",
            )

        avertissement = avertissement_technicien(
            incident["statut"], incident["technicien"]
        )
        if avertissement is not None:
            ajouter_entree_journal(
                journal, "incidents.csv", identifiant,
                "technicien", ligne["technicien"],
                avertissement, "avertissement",
            )

        nb_valides += 1

    return {
        "valides": nb_valides,
        "rejets": nb_rejets,
        "doublons": nb_doublons,
    }
def main() -> None:
    journal = []
    lignes_stations = lire_csv("data/stations.csv")
    lignes_trajets = lire_csv("data/trajets.csv")
    lignes_incidents = lire_csv("data/incidents.csv")

    with engine.begin() as connexion:
        bilan_stations = importer_stations(connexion, lignes_stations, journal)
        stations_connues = recuperer_stations_connues(connexion)
        bilan_trajets = importer_trajets(
            connexion, lignes_trajets, stations_connues, journal
        )
        bilan_incidents = importer_incidents(
            connexion, lignes_incidents, stations_connues, journal
        )

    print("Stations :", bilan_stations)
    print("Trajets :", bilan_trajets)
    print("Incidents :", bilan_incidents)
    ecrire_journal(journal, "docs/journal-import.csv")
if __name__ == "__main__":
    main()
