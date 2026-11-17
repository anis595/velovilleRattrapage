"""Lecture des trajets dans la base."""

from sqlalchemy import Date, cast, func, or_, select

from api.models import Trajet


def lister_trajets(
    session, date_debut, date_fin, station, page, taille_page
):
    """Renvoie une page de trajets selon les filtres demandés."""
    conditions = []

    if date_debut is not None:
        conditions.append(
            cast(Trajet.depart_horodatage, Date) >= date_debut
        )
    if date_fin is not None:
        conditions.append(
            cast(Trajet.depart_horodatage, Date) <= date_fin
        )
    if station is not None:
        conditions.append(
            or_(
                Trajet.station_depart == station,
                Trajet.station_arrivee == station,
            )
        )

    total = session.scalar(
        select(func.count()).select_from(Trajet).where(*conditions)
    )

    trajets = session.scalars(
        select(Trajet)
        .where(*conditions)
        .order_by(Trajet.depart_horodatage, Trajet.trajet_id)
        .offset((page - 1) * taille_page)
        .limit(taille_page)
    ).all()

    return {
        "total": total,
        "page": page,
        "taille_page": taille_page,
        "resultats": trajets,
    }