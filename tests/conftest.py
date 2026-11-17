"""Fixtures pytest communes.

À compléter : client TestClient de l'API, jetons pour exploitant01 et direction01,
session de base de données de test. Aucun secret en dur : lire .env.
"""
"""Fixtures communes des tests."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Fournit un client HTTP pour tester l’API."""
    with TestClient(app) as client_test:
        yield client_test