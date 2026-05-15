"""
tests/api/v1/households/conftest.py — Shared fixtures for household endpoint tests.

Root conftest provides: alice, seth, household, other_household, account.
"""

import pytest
from ninja.testing import TestClient

from api.v1.households import router
from tests.factories import HouseholdFactory


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def shared_household(db, alice, seth):
    """A household shared by alice and seth."""
    h = HouseholdFactory(name='Shared Household')
    h.users.add(alice, seth)
    return h
