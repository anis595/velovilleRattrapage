"""Routeur incidents.

À compléter : GET /incidents (filtre statut, pagination) et
PUT /incidents/{incident_id}/statut (rôle exploitant).
"""
"""Routes de lecture et de changement de statut des incidents."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import IncidentLecture, IncidentsPage, StatutEntree
from api.securite import exiger_role, utilisateur_courant
from api.services.incidents import changer_statut_incident, lister_incidents

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
    dependencies=[Depends(utilisateur_courant)],
)


@router.get("", response_model=IncidentsPage)
def lire_incidents(
    statut: str | None = None,
    page: int = Query(default=1, ge=1),
    taille_page: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db),
):
    """Renvoie les incidents filtrés et paginés."""
    return lister_incidents(session, statut, page, taille_page)


@router.put(
    "/{incident_id}/statut",
    response_model=IncidentLecture,
    dependencies=[Depends(exiger_role("exploitant"))],
)
def modifier_statut(
    incident_id: str,
    donnees: StatutEntree,
    session: Session = Depends(get_db),
):
    """Change le statut d’un incident si la transition est autorisée."""
    try:
        incident = changer_statut_incident(
            session, incident_id, donnees.statut
        )
    except ValueError as erreur:
        raise HTTPException(
            status_code=422,
            detail=str(erreur),
        ) from erreur

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident introuvable",
        )

    return incident