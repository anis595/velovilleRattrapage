"""Authentification et autorisation.

À compléter : vérification d'un mot de passe contre son hachage bcrypt, création et
décodage du JWT (secret et algorithme lus dans l'environnement),
dépendances utilisateur_courant() et exiger_role("exploitant").
"""
"""Authentification et autorisation de l’API VéloVille."""

import bcrypt
import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from api.models import Utilisateur

import jwt

def verifier_mot_de_passe(mot_de_passe, hachage):
    """Compare le mot de passe saisi au hachage stocké."""
    return bcrypt.checkpw(
        mot_de_passe.encode("utf-8"),
        hachage.encode("utf-8"),
    )



def authentifier_utilisateur(session, username, password):
    """Renvoie l’utilisateur si son mot de passe est correct."""
    utilisateur = session.scalar(
        select(Utilisateur).where(Utilisateur.username == username)
    )

    if utilisateur is None:
        return None

    if not verifier_mot_de_passe(
        password, utilisateur.mot_de_passe_hash
    ):
        return None

    return utilisateur
def creer_jeton(username, role):
    """Crée un jeton signé contenant l’identité, le rôle et une expiration."""
    maintenant = datetime.now(timezone.utc)
    expiration = maintenant + timedelta(
        minutes=int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    )

    contenu = {
        "sub": username,
        "role": role,
        "iat": maintenant,
        "exp": expiration,
    }

    return jwt.encode(
        contenu,
        os.environ["JWT_SECRET"],
        algorithm="HS256",
    )

def decoder_jeton(jeton):
    """Vérifie le jeton et renvoie son identité et son rôle."""
    return jwt.decode(
        jeton,
        os.environ["JWT_SECRET"],
        algorithms=["HS256"],
        options={"require": ["sub", "role", "exp"]},
    )

porteur = HTTPBearer(auto_error=False)


def utilisateur_courant(
    identifiants: HTTPAuthorizationCredentials | None = Depends(porteur),
):
    """Renvoie l’identité du jeton ou refuse la requête."""
    erreur_401 = HTTPException(
        status_code=401,
        detail="Identifiants invalides",
    )

    if identifiants is None:
        raise erreur_401

    try:
        contenu = decoder_jeton(identifiants.credentials)
    except jwt.PyJWTError:
        raise erreur_401

    if not contenu.get("sub") or contenu.get("role") not in (
        "exploitant",
        "direction",
    ):
        raise erreur_401

    return contenu


def exiger_role(role_attendu):
    """Autorise seulement le rôle demandé."""

    def verifier_role(utilisateur=Depends(utilisateur_courant)):
        """Vérifie le rôle contenu dans le jeton."""
        if utilisateur["role"] != role_attendu:
            raise HTTPException(
                status_code=403,
                detail="Acces reserve au role exploitant",
            )
        return utilisateur

    return verifier_role