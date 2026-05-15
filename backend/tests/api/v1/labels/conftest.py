"""
tests/api/v1/labels/conftest.py — Shared fixtures for label endpoint tests.

Root conftest provides: alice, seth, household, other_household, label,
other_label, labeled_transaction.
"""

import pytest
from ninja.testing import TestClient

from api.v1.labels import router


@pytest.fixture
def client():
    return TestClient(router)
