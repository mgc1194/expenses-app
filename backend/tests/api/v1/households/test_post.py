"""
tests/api/v1/households/test_post.py — Tests for POST /households/.

Root conftest provides: alice, household.
households/conftest.py provides: client.
"""

import pytest


@pytest.mark.django_db
class TestCreateHousehold:
    def test_creates_household(self, client, alice):
        response = client.post('/households/', json={'name': 'New Household'}, user=alice)
        assert response.status_code == 200
        assert response.json()['name'] == 'New Household'

    def test_creator_is_added_as_member(self, client, alice):
        response = client.post('/households/', json={'name': 'Solo Household'}, user=alice)
        members = [m['email'] for m in response.json()['members']]
        assert alice.email in members

    def test_blank_name_returns_400(self, client, alice):
        response = client.post('/households/', json={'name': '   '}, user=alice)
        assert response.status_code == 400

    def test_duplicate_name_for_same_user_returns_400(self, client, alice, household):
        response = client.post('/households/', json={'name': household.name}, user=alice)
        assert response.status_code == 400

    def test_unauthenticated_returns_401(self, client):
        response = client.post('/households/', json={'name': 'X'})
        assert response.status_code == 401
