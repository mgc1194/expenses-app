"""
tests/api/v1/accounts/test_get.py — Tests for GET /accounts/.

Root conftest provides: alice, seth, household, other_household,
account_type, account.
accounts/conftest.py provides: client, second_household.
"""

import pytest

from tests.factories import AccountFactory


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
