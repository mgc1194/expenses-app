"""
tests/api/v1/labels/test_post.py — Tests for POST /labels/.

Root conftest provides: alice, household, other_household, label.
labels/conftest.py provides: client.
"""

import pytest


@pytest.mark.django_db
class TestCreateLabel:
    def test_creates_label(self, client, alice, household):
        response = client.post(
            '/labels/',
            json={'name': 'Restaurants', 'color': '#FF0000', 'household_id': household.id},
            user=alice,
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'Restaurants'

    def test_duplicate_name_in_same_household_returns_400(self, client, alice, household, label):
        response = client.post(
            '/labels/',
            json={'name': label.name, 'color': '#000000', 'household_id': household.id},
            user=alice,
        )
        assert response.status_code == 400

    def test_blank_name_returns_400(self, client, alice, household):
        response = client.post(
            '/labels/',
            json={'name': '  ', 'color': '#000000', 'household_id': household.id},
            user=alice,
        )
        assert response.status_code == 400

    def test_returns_403_for_non_member_household(self, client, alice, other_household):
        response = client.post(
            '/labels/',
            json={'name': 'Spy Label', 'color': '#000000', 'household_id': other_household.id},
            user=alice,
        )
        assert response.status_code == 403

    def test_unauthenticated_returns_401(self, client, household):
        response = client.post(
            '/labels/',
            json={'name': 'X', 'color': '#000000', 'household_id': household.id},
        )
        assert response.status_code == 401
