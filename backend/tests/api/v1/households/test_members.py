"""
tests/api/v1/households/test_members.py — Tests for household member management.

Covers POST /households/{id}/members/ and DELETE /households/{id}/members/{uid}/.

Root conftest provides: alice, seth, household.
households/conftest.py provides: client, shared_household.
"""

import pytest


@pytest.mark.django_db
class TestAddMember:
    def test_adds_member(self, client, alice, household, seth):
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
