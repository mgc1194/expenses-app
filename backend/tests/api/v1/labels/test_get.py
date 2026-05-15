"""
tests/api/v1/labels/test_get.py — Tests for GET /labels/.

Root conftest provides: alice, household, other_household, label.
labels/conftest.py provides: client.
"""

import pytest

from tests.factories import LabelFactory


@pytest.mark.django_db
class TestListLabels:
    def test_returns_labels_for_users_households(self, client, alice, label):
        response = client.get('/labels/', user=alice)
        assert response.status_code == 200
        assert any(lbl['id'] == label.id for lbl in response.json())

    def test_does_not_return_labels_from_other_households(self, client, alice, other_household):
        LabelFactory(name='Groceries', household=other_household)
        response = client.get('/labels/', user=alice)
        assert response.json() == []

    def test_filters_by_household_id(self, client, alice, household, label):
        response = client.get(f'/labels/?household_id={household.id}', user=alice)
        assert response.status_code == 200
        assert all(lbl['household_id'] == household.id for lbl in response.json())

    def test_returns_403_if_household_belongs_to_other_user(self, client, alice, other_household):
        response = client.get(f'/labels/?household_id={other_household.id}', user=alice)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_household(self, client, alice):
        response = client.get('/labels/?household_id=9999', user=alice)
        assert response.status_code == 404

    def test_returns_empty_list_when_no_labels(self, client, alice, household):
        response = client.get('/labels/', user=alice)
        assert response.json() == []

    def test_unauthenticated_returns_401(self, client):
        response = client.get('/labels/')
        assert response.status_code == 401
