"""
tests/api/v1/test_accounts.py — Tests for account management endpoints.
"""

import pytest
from ninja.testing import TestClient

from api.v1.accounts import router
from tests.factories import AccountFactory, HouseholdFactory
from transactions.models import Account

# ── Module-local fixtures ─────────────────────────────────────────────────────
# Shared conftest provides: alice, seth, household, other_household,
# account_type, account.


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def second_household(db, alice):
    """A second household also belonging to alice."""
    h = HouseholdFactory(name='Alice Second Household')
    h.users.add(alice)
    return h


# ── GET /accounts/ ────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestListAccounts:
    def test_returns_accounts_for_users_households(self, client, alice, account):
        response = client.get('/accounts/', user=alice)
        assert response.status_code == 200
        ids = [a['id'] for a in response.json()]
        assert account.id in ids

    def test_does_not_return_accounts_from_other_households(
        self, client, alice, other_household, account_type
    ):
        AccountFactory(name='Other Account', account_type=account_type, household=other_household)
        response = client.get('/accounts/', user=alice)
        names = [a['name'] for a in response.json()]
        assert 'Other Account' not in names

    def test_filters_by_household_id(self, client, alice, household, account):
        response = client.get(f'/accounts/?household_id={household.id}', user=alice)
        assert response.status_code == 200
        assert all(a['household_id'] == household.id for a in response.json())

    def test_returns_accounts_across_multiple_households(
        self, client, alice, account, second_household, account_type
    ):
        second = AccountFactory(
            name='Second Account', account_type=account_type, household=second_household
        )
        response = client.get('/accounts/', user=alice)
        ids = [a['id'] for a in response.json()]
        assert account.id in ids
        assert second.id in ids

    def test_returns_403_for_non_member_household(self, client, alice, other_household):
        response = client.get(f'/accounts/?household_id={other_household.id}', user=alice)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_household(self, client, alice):
        response = client.get('/accounts/?household_id=9999', user=alice)
        assert response.status_code == 404

    def test_unauthenticated_returns_401(self, client):
        response = client.get('/accounts/')
        assert response.status_code == 401


# ── POST /accounts/ ───────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCreateAccount:
    def test_creates_account(self, client, alice, household, account_type):
        response = client.post(
            '/accounts/',
            json={
                'name': 'My New Account',
                'account_type_id': account_type.id,
                'household_id': household.id,
            },
            user=alice,
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'My New Account'

    def test_duplicate_name_in_same_household_returns_400(
        self, client, alice, account, household, account_type
    ):
        response = client.post(
            '/accounts/',
            json={
                'name': account.name,
                'account_type_id': account_type.id,
                'household_id': household.id,
            },
            user=alice,
        )
        assert response.status_code == 400

    def test_blank_name_returns_400(self, client, alice, household, account_type):
        response = client.post(
            '/accounts/',
            json={
                'name': '   ',
                'account_type_id': account_type.id,
                'household_id': household.id,
            },
            user=alice,
        )
        assert response.status_code == 400

    def test_returns_403_for_non_member_household(
        self, client, alice, other_household, account_type
    ):
        response = client.post(
            '/accounts/',
            json={
                'name': 'Spy Account',
                'account_type_id': account_type.id,
                'household_id': other_household.id,
            },
            user=alice,
        )
        assert response.status_code == 403

    def test_unauthenticated_returns_401(self, client, household, account_type):
        response = client.post(
            '/accounts/',
            json={
                'name': 'X',
                'account_type_id': account_type.id,
                'household_id': household.id,
            },
        )
        assert response.status_code == 401


# ── DELETE /accounts/{id}/ ────────────────────────────────────────────────────


@pytest.mark.django_db
class TestDeleteAccount:
    def test_deletes_account(self, client, alice, account):
        aid = account.id
        response = client.delete(f'/accounts/{aid}/', user=alice)
        assert response.status_code == 204
        assert not Account.objects.filter(pk=aid).exists()

    def test_returns_409_when_account_has_transactions(self, client, alice, transaction):
        response = client.delete(f'/accounts/{transaction.account.id}/', user=alice)
        assert response.status_code == 409

    def test_returns_403_for_non_member(self, client, seth, account):
        response = client.delete(f'/accounts/{account.id}/', user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_account(self, client, alice):
        response = client.delete('/accounts/9999/', user=alice)
        assert response.status_code == 404
