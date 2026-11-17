"""Lecture des stations dans la base."""

from sqlalchemy import func, select

from api.models import Station


def lister_stations(session, commune, page, taille_page):
    """Renvoie une page de stations et le nombre total correspondant."""
    filtre = Station.commune == commune if commune else True

    total = session.scalar(
        select(func.count()).select_from(Station).where(filtre)
    )

    stations = session.scalars(
        select(Station)
        .where(filtre)
        .order_by(Station.station_id)
        .offset((page - 1) * taille_page)
        .limit(taille_page)
    ).all()

    return {
        "total": total,
        "page": page,
        "taille_page": taille_page,
        "resultats": stations,
    }


def trouver_station(session, station_id):
    """Renvoie la station demandée, ou None si elle n’existe pas."""
    return session.get(Station, station_id)