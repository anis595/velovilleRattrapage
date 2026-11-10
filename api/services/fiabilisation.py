"""Règles de fiabilisation des données (module métier testé).

À compléter : fonctions pures, sans accès à la base, qui normalisent ou rejettent
une valeur ou une ligne : horodatages, identifiants de vélo, statuts
d'incident, durées, références de station, cohérence des dates,
doublons. Chaque fonction retourne la valeur normalisée ou signale le
motif de rejet. Ces fonctions sont appelées par scripts/importer.py et
couvertes par tests/unit/.
"""

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


stations = ["S001", "S002"]

print(valider_station("S001", stations))  # S001
print(valider_station("", stations, obligatoire=False))  # None
