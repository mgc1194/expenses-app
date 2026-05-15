"""
tests/api/v1/households/test_get.py — Tests for GET /households/ and GET /households/{id}/.

Root conftest provides: alice, seth, household, other_household.
households/conftest.py provides: client.
"""

import pytest


@pytest.mark.django_db
class TestListHouseholds:
    def test_returns_households_for_user(self, client, alice, household):
        response = client.get('/households/', user=alice)
        assert response.status_code == 200
        ids = [h['id'] for h in response.json()]
        assert household.id in ids

    def test_does_not_return_other_users_households(self, client, alice, other_household):
        response = client.get('/households/', user=alice)
        ids = [h['id'] for h in response.json()]
        assert other_household.id not in ids

    def test_unauthenticated_returns_401(self, client):
        response = client.get('/households/')
        assert response.status_code == 401


@pytest.mark.django_db
class TestGetHousehold:
    def test_returns_household_for_member(self, client, alice, household):
        response = client.get(f'/households/{household.id}/', user=alice)
        assert response.status_code == 200
        assert response.json()['id'] == household.id

    def test_returns_403_for_non_member(self, client, seth, household):
        response = client.get(f'/households/{household.id}/', user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_household(self, client, alice):
        response = client.get('/households/9999/', user=alice)
        assert response.status_code == 404

    def test_response_includes_members(self, client, alice, household):
        response = client.get(f'/households/{household.id}/', user=alice)
        assert response.status_code == 200
        emails = [m['email'] for m in response.json()['members']]
        assert alice.email in emails
