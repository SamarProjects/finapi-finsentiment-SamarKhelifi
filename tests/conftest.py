"""Fixtures partagées entre les tests."""

import pytest

from finapi.app import create_app


@pytest.fixture
def client():
    """Client Flask de test, sans lancer de vrai serveur."""
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()
