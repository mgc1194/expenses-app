"""
tests/api/v1/accounts/conftest.py — Shared fixtures for account endpoint tests.

Root conftest provides: alice, seth, household, other_household,
account_type, account.
"""

import pytest
from ninja.testing import TestClient

from api.v1.accounts import router
from tests.factories import HouseholdFactory


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def second_household(db, alice):
    """A second household also belonging to alice."""
    h = HouseholdFactory(name='Alice Second Household')
    h.users.add(alice)
    return h
