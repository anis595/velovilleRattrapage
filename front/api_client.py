"""Client HTTP commun aux écrans Streamlit."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
API_TIMEOUT_SECONDES = float(os.getenv("API_TIMEOUT_SECONDES", "5"))


class ErreurApi(Exception):
    """Erreur de l’API affichable dans le front."""


def appeler_api(methode, chemin, jeton=None, params=None, donnees=None):
    """Appelle l’API et renvoie sa réponse JSON."""
    entetes = {}
    if jeton:
        entetes["Authorization"] = f"Bearer {jeton}"

    try:
        reponse = requests.request(
            methode,
            f"{API_URL}{chemin}",
            headers=entetes,
            params=params,
            json=donnees,
            timeout=API_TIMEOUT_SECONDES,
        )
    except requests.exceptions.RequestException as erreur:
        raise ErreurApi(
            "L'API est injoignable. Vérifiez qu'elle est démarrée."
        ) from erreur

    if reponse.status_code == 401:
        if chemin == "/auth/login":
            raise ErreurApi("Identifiant ou mot de passe incorrect.")
        raise ErreurApi("Votre session a expiré. Veuillez vous connecter.")

    if reponse.status_code == 403:
        raise ErreurApi(
            "Vous n'avez pas le droit de modifier un incident."
        )

    if reponse.status_code == 404:
        raise ErreurApi("Incident introuvable.")

    if reponse.status_code == 422:
        if methode == "PUT" and chemin.startswith("/incidents/"):
            raise ErreurApi("Transition de statut non autorisée.")
        raise ErreurApi("Paramètres invalides.")

    if not reponse.ok:
        raise ErreurApi("Une erreur est survenue dans l'API.")

    return reponse.json()
