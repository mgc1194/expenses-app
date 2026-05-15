"""
tests/api/v1/households/test_delete.py — Tests for DELETE /households/{id}/.

Root conftest provides: alice, seth, household, account.
households/conftest.py provides: client.
"""

import pytest

from users.models import Household


@pytest.mark.django_db
class TestDeleteHousehold:
    def test_deletes_household(self, client, alice, household):
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
