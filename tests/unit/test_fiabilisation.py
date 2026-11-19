"""Tests unitaires des règles de fiabilisation."""

from datetime import datetime

import pytest

from api.services.fiabilisation import (
    normaliser_identifiant_velo,
    normalise_statut,
    valider_duree,
    normaliser_horodatage_trajet,
    valider_station,
    valider_cible_incident,
    valider_dates_incident,
    valider_capacite,
    convertir_horodatage_incident,
    valider_usager,
    avertissement_technicien,
    est_doublon_exact,
    valider_identifiant_unique,
)

# Identifiants des vélos


@pytest.mark.parametrize(
    "identifiant, attendu",
    [
        ("v1281", "V1281"),
        ("V1281", "V1281"),
    ],
)
def test_normaliser_identifiant_velo(identifiant, attendu):
    assert normaliser_identifiant_velo(identifiant) == attendu


# Statuts des incidents


@pytest.mark.parametrize(
    "statut, attendu",
    [
        ("ouvert", "ouvert"),
        ("Ouvert", "ouvert"),
        ("en cours", "en_cours"),
        ("En cours", "en_cours"),
        ("en_cours", "en_cours"),
        ("Resolu", "resolu"),
        ("RESOLU", "resolu"),
        ("resolu", "resolu"),
    ],
)
def test_normalise_statut(statut, attendu):
    assert normalise_statut(statut) == attendu


@pytest.mark.parametrize("statut", ["", "inconnu", None])
def test_normalise_statut_invalide(statut):
    with pytest.raises(ValueError):
        normalise_statut(statut)


# Durées des trajets


def test_valider_duree_positive():
    resultat = valider_duree("120")

    assert resultat == 120
    assert isinstance(resultat, int)


@pytest.mark.parametrize("duree", ["0", "-10", "abc", "", "1.5"])
def test_valider_duree_invalide(duree):
    with pytest.raises(ValueError):
        valider_duree(duree)


# Horodatages des trajets


@pytest.mark.parametrize(
    "texte",
    [
        "2026-08-24 11:01:00",
        "24/08/2026 11:01",
    ],
)
def test_normaliser_horodatage_trajet(texte):
    attendu = datetime(2026, 8, 24, 11, 1)

    assert normaliser_horodatage_trajet(texte) == attendu


@pytest.mark.parametrize(
    "texte",
    [
        "",
        "date inconnue",
        "2026-02-30 11:01:00",
    ],
)
def test_normaliser_horodatage_trajet_invalide(texte):
    with pytest.raises(ValueError):
        normaliser_horodatage_trajet(texte)


# Références de station


@pytest.mark.parametrize("obligatoire", [True, False])
def test_valider_station_connue(obligatoire):
    assert valider_station("S001", ["S001", "S002"], obligatoire) == "S001"


@pytest.mark.parametrize("reference", ["", None])
def test_valider_station_facultative_absente(reference):
    assert valider_station(reference, ["S001"], obligatoire=False) is None


@pytest.mark.parametrize("reference", ["", None])
def test_valider_station_obligatoire_absente(reference):
    with pytest.raises(ValueError):
        valider_station(reference, ["S001"])


@pytest.mark.parametrize("obligatoire", [True, False])
def test_valider_station_inconnue(obligatoire):
    with pytest.raises(ValueError):
        valider_station("S999", ["S001"], obligatoire)


# Cibles des incidents


@pytest.mark.parametrize(
    "cible, velo_id, station_id",
    [
        ("velo", "V1281", ""),
        ("velo", "V1281", None),
        ("station", "", "S001"),
        ("station", None, "S001"),
    ],
)
def test_valider_cible_incident_valide(cible, velo_id, station_id):
    assert valider_cible_incident(cible, velo_id, station_id, ["S001"]) == cible


@pytest.mark.parametrize(
    "cible, velo_id, station_id",
    [
        ("velo", "", ""),
        ("velo", None, None),
        ("velo", "V1281", "S001"),
        ("station", "V1281", "S001"),
        ("station", "", ""),
        ("station", None, None),
        ("station", "", "S999"),
        ("inconnue", "", ""),
        ("", "", ""),
    ],
)
def test_valider_cible_incident_invalide(cible, velo_id, station_id):
    with pytest.raises(ValueError):
        valider_cible_incident(cible, velo_id, station_id, ["S001"])


# Cohérence des dates des incidents


@pytest.mark.parametrize(
    "resolution",
    [
        datetime(2026, 8, 24, 10, 0),
        datetime(2026, 8, 24, 11, 0),
    ],
)
def test_valider_dates_incident_resolu(resolution):
    signalement = datetime(2026, 8, 24, 10, 0)

    assert valider_dates_incident("resolu", signalement, resolution) == resolution


@pytest.mark.parametrize("statut", ["ouvert", "en_cours"])
def test_valider_dates_incident_non_resolu(statut):
    signalement = datetime(2026, 8, 24, 10, 0)

    assert valider_dates_incident(statut, signalement, None) is None


def test_valider_dates_incident_signalement_absent():
    with pytest.raises(ValueError):
        valider_dates_incident("ouvert", None, None)


def test_valider_dates_incident_resolu_sans_resolution():
    signalement = datetime(2026, 8, 24, 10, 0)

    with pytest.raises(ValueError):
        valider_dates_incident("resolu", signalement, None)


@pytest.mark.parametrize("statut", ["ouvert", "en_cours"])
def test_valider_dates_incident_non_resolu_avec_resolution(statut):
    signalement = datetime(2026, 8, 24, 10, 0)
    resolution = datetime(2026, 8, 24, 11, 0)

    with pytest.raises(ValueError):
        valider_dates_incident(statut, signalement, resolution)


def test_valider_dates_incident_resolution_anterieure():
    signalement = datetime(2026, 8, 24, 10, 0)
    resolution = datetime(2026, 8, 24, 9, 0)

    with pytest.raises(ValueError):
        valider_dates_incident("resolu", signalement, resolution)


# Capacité des stations


def test_valider_capacite_positive():
    resultat = valider_capacite("20")

    assert resultat == 20
    assert isinstance(resultat, int)


@pytest.mark.parametrize("capacite", ["0", "-5", "abc", "", "2.5"])
def test_valider_capacite_invalide(capacite):
    with pytest.raises(ValueError):
        valider_capacite(capacite)


# Conversion des horodatages des incidents


def test_convertir_horodatage_incident():
    assert convertir_horodatage_incident("2026-08-24 10:30") == datetime(
        2026, 8, 24, 10, 30
    )


@pytest.mark.parametrize("texte", ["", None])
def test_convertir_horodatage_incident_absent(texte):
    assert convertir_horodatage_incident(texte) is None


@pytest.mark.parametrize(
    "texte",
    [
        "date inconnue",
        "2026-02-30 10:30",
    ],
)
def test_convertir_horodatage_incident_invalide(texte):
    with pytest.raises(ValueError):
        convertir_horodatage_incident(texte)


# Usagers


def test_valider_usager_abonne():
    assert valider_usager("abonne", "U12ab34cd") == "U12ab34cd"


@pytest.mark.parametrize("reference", ["", None])
def test_valider_usager_occasionnel(reference):
    assert valider_usager("occasionnel", reference) is None


@pytest.mark.parametrize("reference", ["", None])
def test_valider_usager_abonne_sans_reference(reference):
    with pytest.raises(ValueError):
        valider_usager("abonne", reference)


def test_valider_usager_occasionnel_avec_reference():
    with pytest.raises(ValueError):
        valider_usager("occasionnel", "U12ab34cd")


@pytest.mark.parametrize("type_usager", ["inconnu", "", None])
def test_valider_usager_type_invalide(type_usager):
    with pytest.raises(ValueError):
        valider_usager(type_usager, "")


# Avertissements concernant le technicien


@pytest.mark.parametrize("statut", ["en_cours", "resolu"])
@pytest.mark.parametrize("technicien", ["", None])
def test_avertissement_technicien_absent(statut, technicien):
    assert (
        avertissement_technicien(statut, technicien)
        == "Technicien absent après prise en charge"
    )


@pytest.mark.parametrize(
    "statut, technicien",
    [
        ("ouvert", ""),
        ("ouvert", None),
        ("ouvert", "Samir"),
        ("en_cours", "Samir"),
        ("resolu", "Samir"),
    ],
)
def test_avertissement_technicien_non_necessaire(statut, technicien):
    assert avertissement_technicien(statut, technicien) is None


# Doublons exacts


def test_est_doublon_exact():
    ligne = {"station_id": "S001", "capacite": "20"}
    lignes_deja_vues = [{"station_id": "S001", "capacite": "20"}]

    assert est_doublon_exact(ligne, lignes_deja_vues) is True


def test_est_doublon_exact_liste_vide():
    ligne = {"station_id": "S001", "capacite": "20"}

    assert est_doublon_exact(ligne, []) is False


def test_meme_identifiant_mais_ligne_differente():
    ligne = {"station_id": "S001", "capacite": "30"}
    lignes_deja_vues = [{"station_id": "S001", "capacite": "20"}]

    assert est_doublon_exact(ligne, lignes_deja_vues) is False


def test_est_doublon_exact_ne_modifie_pas_les_donnees():
    ligne = {"station_id": "S002", "capacite": "30"}
    lignes_deja_vues = [{"station_id": "S001", "capacite": "20"}]

    est_doublon_exact(ligne, lignes_deja_vues)

    assert ligne == {"station_id": "S002", "capacite": "30"}
    assert lignes_deja_vues == [{"station_id": "S001", "capacite": "20"}]


# Unicité des identifiants


def test_valider_identifiant_unique():
    identifiants = ["S001"]

    assert valider_identifiant_unique("S002", identifiants) == "S002"
    assert identifiants == ["S001"]


@pytest.mark.parametrize("identifiant", ["", None])
def test_valider_identifiant_unique_absent(identifiant):
    with pytest.raises(ValueError):
        valider_identifiant_unique(identifiant, [])


def test_valider_identifiant_unique_deja_utilise():
    with pytest.raises(ValueError):
        valider_identifiant_unique("S001", ["S001"])
