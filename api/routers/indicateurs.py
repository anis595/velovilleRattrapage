"""Routes des trois indicateurs VéloVille."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import (
    ActiviteParJourSortie,
    IncidentsParStatutSortie,
    StationsActivesSortie,
)
from api.securite import utilisateur_courant
from api.services.indicateurs import (
    activite_par_jour,
    incidents_par_statut,
    stations_actives,
)

router = APIRouter(
    prefix="/indicateurs",
    tags=["indicateurs"],
    dependencies=[Depends(utilisateur_courant)],
)


@router.get("/activite-par-jour", response_model=ActiviteParJourSortie)
def lire_activite_par_jour(
    date_debut: date | None = None,
    date_fin: date | None = None,
    session: Session = Depends(get_db),
):
    """Renvoie le nombre de trajets pour chaque jour de la période."""
    return {
        "donnees": activite_par_jour(session, date_debut, date_fin)
    }


@router.get("/stations-actives", response_model=StationsActivesSortie)
def lire_stations_actives(
    limite: int = Query(default=10, ge=1),
    session: Session = Depends(get_db),
):
    """Renvoie les stations ayant le plus de mouvements."""
    return {"donnees": stations_actives(session, limite)}


@router.get(
    "/incidents-par-statut",
    response_model=IncidentsParStatutSortie,
)
def lire_incidents_par_statut(session: Session = Depends(get_db)):
    """Renvoie les effectifs par statut et le délai moyen de résolution."""
    return incidents_par_statut(session)
