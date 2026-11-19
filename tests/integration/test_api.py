"""Tests des routes publiques et protégées de l’API."""

import os


def test_sante(client):
    """Vérifie que l’API répond sans jeton."""
    reponse = client.get("/sante")

    assert reponse.status_code == 200
    assert reponse.json() == {"statut": "ok"}


def test_login_reussi(client):
    """Vérifie la connexion d’un compte fourni par le TP."""
    reponse = client.post(
        "/auth/login",
        json={
            "username": "exploitant01",
            "password": os.environ["TEST_PASSWORD"],
        },
    )

    assert reponse.status_code == 200
    contenu = reponse.json()
    assert contenu["access_token"]
    assert contenu["token_type"] == "bearer"
    assert contenu["role"] == "exploitant"


def test_login_refuse(client):
    """Vérifie le refus d’un mot de passe incorrect."""
    reponse = client.post(
        "/auth/login",
        json={"username": "exploitant01", "password": "incorrect"},
    )

    assert reponse.status_code == 401
    assert reponse.json() == {"detail": "Identifiants invalides"}


def test_stations_sans_jeton(client):
    """Vérifie qu’une route protégée refuse l’accès anonyme."""
    reponse = client.get("/stations")

    assert reponse.status_code == 401


def test_direction_ne_modifie_pas_incident(client):
    """Vérifie que le rôle direction ne peut pas changer un statut."""
    connexion = client.post(
        "/auth/login",
        json={
            "username": "direction01",
            "password": os.environ["TEST_PASSWORD"],
        },
    )
    assert connexion.status_code == 200
    jeton = connexion.json()["access_token"]

    reponse = client.put(
        "/incidents/I2026-0001/statut",
        json={"statut": "resolu"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 403
    assert reponse.json() == {
        "detail": "Acces reserve au role exploitant"
    }
