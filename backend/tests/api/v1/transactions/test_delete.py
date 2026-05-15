"""
tests/api/v1/transactions/test_delete.py — Tests for DELETE /transactions/{id}/.

Root conftest provides: alice, seth, transaction.
transactions/conftest.py provides: client.
"""

import pytest

from transactions.models import Transaction


@pytest.mark.django_db
class TestDeleteTransaction:
    def test_deletes_transaction(self, client, alice, transaction):
        response = client.delete(f'/transactions/{transaction.id}/', user=alice)
        assert response.status_code == 204
        assert not Transaction.objects.filter(pk=transaction.id).exists()

    def test_returns_403_for_non_member(self, client, seth, transaction):
        response = client.delete(f'/transactions/{transaction.id}/', user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_transaction(self, client, alice):
        response = client.delete('/transactions/9999/', user=alice)
        assert response.status_code == 404
