"""Routes de lecture des stations."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import StationLecture, StationsPage
from api.securite import utilisateur_courant
from api.services.stations import lister_stations, trouver_station

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
    dependencies=[Depends(utilisateur_courant)],
)


@router.get("", response_model=StationsPage)
def lire_stations(
    commune: str | None = None,
    page: int = Query(default=1, ge=1),
    taille_page: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db),
):
    """Renvoie les stations filtrées et paginées."""
    return lister_stations(session, commune, page, taille_page)


@router.get("/{station_id}", response_model=StationLecture)
def lire_station(station_id: str, session: Session = Depends(get_db)):
    """Renvoie une station ou une erreur 404."""
    station = trouver_station(session, station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Station introuvable")
    return station