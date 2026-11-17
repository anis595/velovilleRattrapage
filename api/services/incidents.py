"""Lecture et changement de statut des incidents."""

from datetime import datetime, timezone

from sqlalchemy import func, select

from api.models import Incident


def lister_incidents(session, statut, page, taille_page):
    """Renvoie une page d’incidents, éventuellement filtrée par statut."""
    conditions = []
    if statut is not None:
        conditions.append(Incident.statut == statut)

    total = session.scalar(
        select(func.count()).select_from(Incident).where(*conditions)
    )

    incidents = session.scalars(
        select(Incident)
        .where(*conditions)
        .order_by(
            Incident.date_signalement.desc(),
            Incident.incident_id,
        )
        .offset((page - 1) * taille_page)
        .limit(taille_page)
    ).all()

    return {
        "total": total,
        "page": page,
        "taille_page": taille_page,
        "resultats": incidents,
    }


def changer_statut_incident(session, incident_id, nouveau_statut):
    """Applique une transition autorisée et renvoie l’incident modifié."""
    incident = session.get(Incident, incident_id)
    if incident is None:
        return None

    transitions = {
        "ouvert": {"en_cours", "resolu"},
        "en_cours": {"resolu"},
        "resolu": set(),
    }
    if nouveau_statut not in transitions[incident.statut]:
        raise ValueError("Transition de statut non autorisee")

    incident.statut = nouveau_statut
    if nouveau_statut == "resolu" and incident.date_resolution is None:
        incident.date_resolution = datetime.now(timezone.utc).replace(
            tzinfo=None
        )

    session.commit()
    session.refresh(incident)
    return incident