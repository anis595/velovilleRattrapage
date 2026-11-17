"""Routeur auth.

À compléter : POST /auth/login.
"""
"""Route de connexion à l’API VéloVille."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import ConnexionEntree, ConnexionSortie
from api.securite import authentifier_utilisateur, creer_jeton

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ConnexionSortie)
def login(donnees: ConnexionEntree, session: Session = Depends(get_db)):
    """Vérifie les identifiants et renvoie un jeton."""
    utilisateur = authentifier_utilisateur(
        session, donnees.username, donnees.password
    )
    if utilisateur is None:
        raise HTTPException(
            status_code=401,
            detail="Identifiants invalides",
        )

    return ConnexionSortie(
        access_token=creer_jeton(utilisateur.username, utilisateur.role),
        role=utilisateur.role,
    )