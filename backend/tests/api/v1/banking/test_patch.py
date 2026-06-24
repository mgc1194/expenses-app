"""
tests/api/v1/banking/test_patch.py — Tests for PATCH /accounts/{id}/.

Root conftest provides: alice, seth, account.
banking/conftest.py provides: client.
"""

import pytest


@pytest.mark.django_db
class TestRenameAccount:
    def test_renames_account(self, client, alice, account):
        response = client.patch(f'/accounts/{account.id}/', json={'name': 'Renamed'}, user=alice)
        assert response.status_code == 200
        assert response.json()['name'] == 'Renamed'

    def test_blank_name_returns_400(self, client, alice, account):
        response = client.patch(f'/accounts/{account.id}/', json={'name': '   '}, user=alice)
        assert response.status_code == 400

    def test_duplicate_name_in_same_household_returns_400(
        self, client, alice, account, household, account_type
    ):
        from tests.factories import AccountFactory

        other = AccountFactory(name='Other Account', account_type=account_type, household=household)
        response = client.patch(f'/accounts/{account.id}/', json={'name': other.name}, user=alice)
        assert response.status_code == 400

    def test_returns_403_for_non_member(self, client, seth, account):
        response = client.patch(f'/accounts/{account.id}/', json={'name': 'X'}, user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_account(self, client, alice):
        response = client.patch('/accounts/9999/', json={'name': 'X'}, user=alice)
        assert response.status_code == 404
