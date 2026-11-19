"""Entrées et sorties de l’API VéloVille."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StationLecture(BaseModel):
    """Décrit une station renvoyée par l’API."""

    model_config = ConfigDict(from_attributes=True)

    station_id: str
    nom: str
    capacite: int
    latitude: Decimal | None
    longitude: Decimal | None
    date_mise_en_service: date | None
    commune: str


class TrajetLecture(BaseModel):
    """Décrit un trajet renvoyé par l’API."""

    model_config = ConfigDict(from_attributes=True)

    trajet_id: str
    station_depart: str
    station_arrivee: str | None
    depart_horodatage: datetime
    duree_secondes: int
    type_usager: str
    velo_id: str
    usager_ref: str | None


class IncidentLecture(BaseModel):
    """Décrit un incident renvoyé par l’API."""

    model_config = ConfigDict(from_attributes=True)

    incident_id: str
    date_signalement: datetime
    velo_id: str | None
    station_id: str | None
    date_resolution: datetime | None
    technicien: str | None
    statut: str
    cible: str
    type_incident: str


class StationsPage(BaseModel):
    """Contient une page de stations et son total."""

    total: int
    page: int
    taille_page: int
    resultats: list[StationLecture]


class TrajetsPage(BaseModel):
    """Contient une page de trajets et son total."""

    total: int
    page: int
    taille_page: int
    resultats: list[TrajetLecture]


class IncidentsPage(BaseModel):
    """Contient une page d’incidents et son total."""

    total: int
    page: int
    taille_page: int
    resultats: list[IncidentLecture]


class ConnexionEntree(BaseModel):
    """Reçoit les identifiants de connexion."""

    username: str
    password: str


class ConnexionSortie(BaseModel):
    """Renvoie le jeton et le rôle après connexion."""

    access_token: str
    token_type: str = "bearer"
    role: str


class StatutEntree(BaseModel):
    """Reçoit le nouveau statut d’un incident."""

    statut: str


class ActiviteJour(BaseModel):
    jour: date
    nb_trajets: int


class ActiviteParJourSortie(BaseModel):
    donnees: list[ActiviteJour]


class StationActive(BaseModel):
    station_id: str
    nom: str
    nb_departs: int
    nb_arrivees: int


class StationsActivesSortie(BaseModel):
    donnees: list[StationActive]


class IncidentsStatut(BaseModel):
    statut: str
    nb_incidents: int


class IncidentsParStatutSortie(BaseModel):
    donnees: list[IncidentsStatut]
    delai_moyen_resolution_heures: float | None