"""
tests/api/v1/accounts/test_delete.py — Tests for DELETE /accounts/{id}/.

Root conftest provides: alice, seth, account, transaction.
accounts/conftest.py provides: client.
"""

import pytest

from transactions.models import Account


@pytest.mark.django_db
class TestDeleteAccount:
    def test_deletes_account(self, client, alice, account):
        aid = account.id
        response = client.delete(f'/accounts/{aid}/', user=alice)
        assert response.status_code == 204
        assert not Account.objects.filter(pk=aid).exists()

    def test_returns_409_when_account_has_transactions(self, client, alice, transaction):
        response = client.delete(f'/accounts/{transaction.account.id}/', user=alice)
        assert response.status_code == 409

    def test_returns_403_for_non_member(self, client, seth, account):
        response = client.delete(f'/accounts/{account.id}/', user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_account(self, client, alice):
        response = client.delete('/accounts/9999/', user=alice)
        assert response.status_code == 404
