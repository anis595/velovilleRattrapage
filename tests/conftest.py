"""Fixtures communes des tests."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Fournit un client HTTP pour tester l’API."""
    with TestClient(app) as client_test:
        yield client_test
