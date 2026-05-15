"""
tests/api/v1/conftest.py — Shared TestClient for all API v1 tests.

The router-level client is defined here so every sub-package can import it
without re-declaring it. Individual endpoint packages that need a different
router (e.g. summary, which goes through Django's full test client) define
their own client fixture in their own conftest.py.
"""

import pytest
from ninja.testing import TestClient

from api.v1.transactions import router as transactions_router


@pytest.fixture
def client():
    return TestClient(transactions_router)
