"""
tests/api/v1/households/test_patch.py — Tests for PATCH /households/{id}/.

Root conftest provides: alice, seth, household.
households/conftest.py provides: client.
"""

import pytest


@pytest.mark.django_db
class TestRenameHousehold:
    def test_renames_household(self, client, alice, household):
        response = client.patch(
            f'/households/{household.id}/', json={'name': 'Renamed'}, user=alice
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'Renamed'

    def test_blank_name_returns_400(self, client, alice, household):
        response = client.patch(f'/households/{household.id}/', json={'name': '   '}, user=alice)
        assert response.status_code == 400

    def test_returns_403_for_non_member(self, client, seth, household):
        response = client.patch(f'/households/{household.id}/', json={'name': 'X'}, user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_household(self, client, alice):
        response = client.patch('/households/9999/', json={'name': 'X'}, user=alice)
        assert response.status_code == 404
