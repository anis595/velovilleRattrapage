"""Modèles ORM SQLAlchemy : Station, Trajet, Incident, Utilisateur.

À compléter : déclarer les quatre tables conformément à sql/schema.sql.
"""
"""Modèles des quatre tables de VéloVille."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Station(Base):
    """Représente une station de vélos."""

    __tablename__ = "station"

    station_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    nom: Mapped[str] = mapped_column(String(60), nullable=False)
    capacite: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(8, 5))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(8, 5))
    date_mise_en_service: Mapped[date | None] = mapped_column(Date)
    commune: Mapped[str] = mapped_column(String(40), nullable=False)


class Trajet(Base):
    """Représente un trajet effectué à vélo."""

    __tablename__ = "trajet"

    trajet_id: Mapped[str] = mapped_column(String(12), primary_key=True)
    station_depart: Mapped[str] = mapped_column(
        ForeignKey("station.station_id"), nullable=False
    )
    station_arrivee: Mapped[str | None] = mapped_column(
        ForeignKey("station.station_id")
    )
    depart_horodatage: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duree_secondes: Mapped[int] = mapped_column(Integer, nullable=False)
    type_usager: Mapped[str] = mapped_column(String(12), nullable=False)
    velo_id: Mapped[str] = mapped_column(String(8), nullable=False)
    usager_ref: Mapped[str | None] = mapped_column(String(9))


class Incident(Base):
    """Représente un incident signalé sur un vélo ou une station."""

    __tablename__ = "incident"

    incident_id: Mapped[str] = mapped_column(String(12), primary_key=True)
    date_signalement: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    velo_id: Mapped[str | None] = mapped_column(String(8))
    station_id: Mapped[str | None] = mapped_column(ForeignKey("station.station_id"))
    date_resolution: Mapped[datetime | None] = mapped_column(DateTime)
    technicien: Mapped[str | None] = mapped_column(String(40))
    statut: Mapped[str] = mapped_column(String(8), nullable=False)
    cible: Mapped[str] = mapped_column(String(8), nullable=False)
    type_incident: Mapped[str] = mapped_column(String(30), nullable=False)


class Utilisateur(Base):
    """Représente un compte autorisé à utiliser l’API."""

    __tablename__ = "utilisateur"

    id_utilisateur: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    mot_de_passe_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)