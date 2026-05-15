"""
tests/api/v1/labels/test_delete.py — Tests for DELETE /labels/{id}/.

Root conftest provides: alice, seth, label, labeled_transaction.
labels/conftest.py provides: client.
"""

import pytest

from transactions.models import Label


@pytest.mark.django_db
class TestDeleteLabel:
    def test_deletes_label(self, client, alice, label):
        lid = label.id
        response = client.delete(f'/labels/{lid}/', user=alice)
        assert response.status_code == 204
        assert not Label.objects.filter(pk=lid).exists()

    def test_labeled_transactions_are_preserved_with_null_label(
        self, client, alice, labeled_transaction, label
    ):
        client.delete(f'/labels/{label.id}/', user=alice)
        labeled_transaction.refresh_from_db()
        assert labeled_transaction.label is None

    def test_returns_403_for_non_member(self, client, seth, label):
        response = client.delete(f'/labels/{label.id}/', user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_label(self, client, alice):
        response = client.delete('/labels/9999/', user=alice)
        assert response.status_code == 404
