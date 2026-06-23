"""
tests/api/v1/banking/conftest.py — Shared fixtures for banking endpoint tests.

Renamed from tests/api/v1/accounts/conftest.py as part of the banking app
extraction. Router import updated; fixtures unchanged.

Root conftest provides: alice, seth, household, other_household,
account_type, account.
"""

import pytest
from ninja.testing import TestClient

from api.v1.banking import router
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
