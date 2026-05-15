"""
tests/api/v1/test_households.py — Tests for household management endpoints.
"""

import pytest
from ninja.testing import TestClient

from api.v1.households import router
from tests.factories import HouseholdFactory

# ── Module-local fixtures ─────────────────────────────────────────────────────
# Shared conftest provides: alice, seth, household, other_household.


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def shared_household(db, alice, seth):
    """A household shared by alice and seth."""
    h = HouseholdFactory(name='Shared Household')
    h.users.add(alice, seth)
    return h


# ── GET /households/ ──────────────────────────────────────────────────────────


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


# ── POST /households/ ─────────────────────────────────────────────────────────


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


# ── PATCH /households/{id}/ ───────────────────────────────────────────────────


@pytest.mark.django_db
class TestRenameHousehold:
    def test_renames_household(self, client, alice, household):
        response = client.patch(
            f'/households/{household.id}/', json={'name': 'Renamed'}, user=alice
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'Renamed'

    def test_returns_403_for_non_member(self, client, seth, household):
        response = client.patch(f'/households/{household.id}/', json={'name': 'X'}, user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_household(self, client, alice):
        response = client.patch('/households/9999/', json={'name': 'X'}, user=alice)
        assert response.status_code == 404


# ── DELETE /households/{id}/ ──────────────────────────────────────────────────


@pytest.mark.django_db
class TestDeleteHousehold:
    def test_deletes_household(self, client, alice, household):
        from users.models import Household

        hid = household.id
        response = client.delete(f'/households/{hid}/', user=alice)
        assert response.status_code == 204
        assert not Household.objects.filter(pk=hid).exists()

    def test_returns_409_when_household_has_accounts(self, client, alice, household, account):
        response = client.delete(f'/households/{household.id}/', user=alice)
        assert response.status_code == 409

    def test_returns_403_for_non_member(self, client, seth, household):
        response = client.delete(f'/households/{household.id}/', user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_household(self, client, alice):
        response = client.delete('/households/9999/', user=alice)
        assert response.status_code == 404


# ── POST /households/{id}/members/ ───────────────────────────────────────────


@pytest.mark.django_db
class TestAddMember:
    def test_adds_member(self, client, alice, household, seth):
        # seth belongs to other_household by default; add him to alice's too
        response = client.post(
            f'/households/{household.id}/members/',
            json={'email': seth.email},
            user=alice,
        )
        assert response.status_code == 200
        emails = [m['email'] for m in response.json()['members']]
        assert seth.email in emails

    def test_returns_400_for_unknown_email(self, client, alice, household):
        response = client.post(
            f'/households/{household.id}/members/',
            json={'email': 'nobody@example.com'},
            user=alice,
        )
        assert response.status_code == 400

    def test_returns_400_if_already_a_member(self, client, alice, household):
        response = client.post(
            f'/households/{household.id}/members/',
            json={'email': alice.email},
            user=alice,
        )
        assert response.status_code == 400

    def test_returns_403_for_non_member(self, client, seth, household):
        response = client.post(
            f'/households/{household.id}/members/',
            json={'email': seth.email},
            user=seth,
        )
        assert response.status_code == 403


# ── DELETE /households/{id}/members/{uid}/ ────────────────────────────────────


@pytest.mark.django_db
class TestRemoveMember:
    def test_member_can_leave(self, client, alice, shared_household, seth):
        response = client.delete(
            f'/households/{shared_household.id}/members/{alice.id}/', user=alice
        )
        assert response.status_code == 200
        emails = [m['email'] for m in response.json()['members']]
        assert alice.email not in emails

    def test_cannot_remove_last_member(self, client, alice, household):
        response = client.delete(f'/households/{household.id}/members/{alice.id}/', user=alice)
        assert response.status_code == 400

    def test_returns_403_for_non_member(self, client, seth, household, alice):
        response = client.delete(f'/households/{household.id}/members/{alice.id}/', user=seth)
        assert response.status_code == 403


# ── Account count in household detail ────────────────────────────────────────


@pytest.mark.django_db
class TestHouseholdAccountCount:
    def test_account_count_reflects_accounts(self, client, alice, household, account):
        response = client.get(f'/households/{household.id}/', user=alice)
        assert response.status_code == 200
