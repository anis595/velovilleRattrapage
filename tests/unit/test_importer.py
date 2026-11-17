"""Vérifie la traçabilité des doublons exacts à l'import."""

import pytest

from scripts import importer


@pytest.mark.parametrize(
    "nom, identifiant, ligne",
    [
        (
            "station",
            "station_id",
            {
                "station_id": "S001", "nom": "Station A", "commune": "Lille",
                "capacite": "10", "latitude": "", "longitude": "",
                "date_mise_en_service": "",
            },
        ),
        (
            "trajet",
            "trajet_id",
            {
                "trajet_id": "T1", "velo_id": "V001",
                "depart_horodatage": "2026-08-24 08:00:00",
                "station_depart": "S001", "station_arrivee": "",
                "duree_secondes": "120", "type_usager": "occasionnel",
                "usager_ref": "",
            },
        ),
        (
            "incident",
            "incident_id",
            {
                "incident_id": "I1", "date_signalement": "2026-08-24 08:00",
                "cible": "velo", "velo_id": "V001", "station_id": "",
                "type_incident": "panne", "statut": "ouvert",
                "date_resolution": "", "technicien": "",
            },
        ),
    ],
)
def test_doublon_exact_journalise_une_fois(monkeypatch, nom, identifiant, ligne):
    """Une seconde ligne identique est écartée et tracée dans le journal."""
    insertions = []
    monkeypatch.setattr(
        importer, f"inserer_{nom}", lambda connexion, valeur: insertions.append(valeur)
    )
    journal = []
    lignes = [ligne, dict(ligne)]

    if nom == "station":
        bilan = importer.importer_stations(None, lignes, journal)
    else:
        fonction = getattr(importer, f"importer_{nom}s")
        bilan = fonction(None, lignes, ["S001"], journal)

    assert bilan == {"valides": 1, "rejets": 0, "doublons": 1}
    assert len(insertions) == 1
    assert len(journal) == 1
    assert journal[0] == {
        "fichier_source": f"{nom}s.csv",
        "identifiant": ligne[identifiant],
        "colonne": identifiant,
        "valeur": ligne[identifiant],
        "motif": "Doublon exact écarté",
        "decision": "rejet",
    }
