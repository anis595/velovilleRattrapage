"""Valide et normalise les données avant import."""

from datetime import datetime


def normaliser_identifiant_velo(identifiant: str):
    resultat = identifiant.upper()
    return resultat


# print(normaliser_identifiant_velo("v1281"))


def normalise_statut(statut):
    if statut == "ouvert" or statut == "Ouvert":
        return "ouvert"
    elif statut == "en cours" or statut == "En cours" or statut == "en_cours":
        return "en_cours"
    elif statut == "Resolu" or statut == "RESOLU" or statut == "resolu":
        return "resolu"
    else:
        raise ValueError("Statut d'incident invalide")


# print(normalise_statut("Ouvert"))
# print(normalise_statut("En cours"))
# print(normalise_statut("RESOLU"))
# print(normalise_statut("resolu"))


def valider_duree(duree):
    resultat = int(duree)
    if resultat <= 0:
        raise ValueError("La durée doit être strictement positive")
    return resultat


# print(valider_duree("123"))
# print(valider_duree("-123"))


def normaliser_horodatage_trajet(texte):
    try:
        date_converti = datetime.strptime(texte, "%Y-%m-%d %H:%M:%S")
        return date_converti
    except ValueError:
        date_converti = datetime.strptime(texte, "%d/%m/%Y %H:%M")
        return date_converti


# print(normaliser_horodatage_trajet("2026-08-24 11:01:00"))
# print(normaliser_horodatage_trajet("24/08/2026 11:01"))


def valider_station(reference, stations_connues, obligatoire=True):
    if reference == "" or reference is None:
        if obligatoire:
            raise ValueError("Station obligatoire absente")
        return None

    if reference not in stations_connues:
        raise ValueError("Station inconnue")

    return reference


# stations = ["S001", "S002"]

# print(valider_station("S001", stations))
# print(valider_station("", stations, obligatoire=False))


def valider_cible_incident(cible, velo_id, station_id, stations_connues):
    if cible == "velo":
        if velo_id == "" or velo_id is None:
            raise ValueError("Identifiant vélo obligatoire")

        if station_id != "" and station_id is not None:
            raise ValueError("Une cible vélo ne doit pas avoir de station")

    elif cible == "station":
        if velo_id != "" and velo_id is not None:
            raise ValueError("Une cible station ne doit pas avoir de vélo")
        valider_station(station_id, stations_connues)

    else:
        raise ValueError("Cible d'incident invalide")

    return cible


def valider_dates_incident(statut, date_signalement, date_resolution):
    if date_signalement is None:
        raise ValueError("Date de signalement obligatoire")

    # Statut résolu ET résolution absente
    if statut == "resolu" and date_resolution is None:
        raise ValueError("Date de résolution obligatoire")

    # Statut non résolu ET résolution

    if statut != "resolu" and date_resolution is not None:
        raise ValueError("Résolution interdite pour un incident non résolu")

    if date_resolution is not None:
        # Résolution strictement antérieure au signalement
        if date_resolution < date_signalement:
            raise ValueError("Résolution antérieure au signalement")

    return date_resolution


def valider_capacite(capacite):
    resultat = int(capacite)

    if resultat <= 0:
        raise ValueError("La capacité doit être strictement positive")

    return resultat


def convertir_horodatage_incident(texte):
    if texte == "" or texte is None:
        return None
    # Si texte est vide ou vaut None :
    #     retourner None
    date_converti = datetime.strptime(texte, "%Y-%m-%d %H:%M")
    # Convertir avec datetime.strptime et le format "%Y-%m-%d %H:%M"

    return date_converti


def valider_usager(type_usager, usager_ref):
    if type_usager != "abonne" and type_usager != "occasionnel":
        raise ValueError("Type d'usager invalide")

    if type_usager == "abonne":
        if usager_ref == "" or usager_ref is None:
            raise ValueError("Pseudonyme obligatoire pour un abonné")

        return usager_ref

    if usager_ref != "" and usager_ref is not None:
        raise ValueError("Un usager occasionnel ne doit pas avoir de pseudonyme")

    return None


def avertissement_technicien(statut, technicien):
    if statut == "en_cours" or statut == "resolu":
        if technicien == "" or technicien is None:
            return "Technicien absent après prise en charge"

    return None


def est_doublon_exact(ligne, lignes_deja_vues):
    if ligne in lignes_deja_vues:
        return True
    else:
        return False


def valider_identifiant_unique(identifiant, identifiants_deja_vus):
    if identifiant == "" or identifiant is None:
        raise ValueError("Identifiant obligatoire")

    if identifiant in identifiants_deja_vus:
        raise ValueError("Identifiant déjà utilisé")

    return identifiant
