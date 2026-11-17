"""Connexion à PostgreSQL (SQLAlchemy 2).

À compléter : lire DATABASE_URL depuis l'environnement (.env), créer l'engine, la
fabrique de sessions et la dépendance get_db() utilisée par les routeurs.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Fournit une session à une route, puis la ferme."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
