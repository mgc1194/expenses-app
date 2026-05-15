"""
tests/api/v1/accounts/test_post.py — Tests for POST /accounts/.

Root conftest provides: alice, seth, household, other_household, account_type, account.
accounts/conftest.py provides: client.
"""

import pytest


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
