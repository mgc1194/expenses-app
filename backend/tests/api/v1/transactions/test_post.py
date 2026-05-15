"""
tests/api/v1/transactions/test_post.py — Tests for POST /transactions/.

Root conftest provides: alice, seth, household, account_type, account.
transactions/conftest.py provides: client.
"""

import pytest

from transactions.models import Transaction


@pytest.mark.django_db
class TestCreateTransaction:
    def test_creates_transaction_successfully(self, client, alice, account):
        response = client.post(
            '/transactions/',
            json={
                'account_id': account.id,
                'date': '2026-02-01',
                'concept': 'WHOLE FOODS',
                'amount': -55.00,
            },
            user=alice,
        )
        assert response.status_code == 200
        data = response.json()
        assert data['concept'] == 'WHOLE FOODS'
        assert data['amount'] == -55.00
        assert data['account_name'] == account.name

    def test_persists_to_database(self, client, alice, account):
        client.post(
            '/transactions/',
            json={
                'account_id': account.id,
                'date': '2026-02-01',
                'concept': 'WHOLE FOODS',
                'amount': -55.00,
            },
            user=alice,
        )
        assert Transaction.objects.filter(concept='WHOLE FOODS', account=account).exists()

    def test_returns_400_for_blank_concept(self, client, alice, account):
        response = client.post(
            '/transactions/',
            json={'account_id': account.id, 'date': '2026-02-01', 'concept': '  ', 'amount': -5},
            user=alice,
        )
        assert response.status_code == 400

    def test_returns_400_for_duplicate(self, client, alice, account):
        payload = {
            'account_id': account.id,
            'date': '2026-02-01',
            'concept': 'WHOLE FOODS',
            'amount': -55.00,
        }
        client.post('/transactions/', json=payload, user=alice)
        response = client.post('/transactions/', json=payload, user=alice)
        assert response.status_code == 400

    def test_returns_403_for_non_member(self, client, seth, account):
        response = client.post(
            '/transactions/',
            json={
                'account_id': account.id,
                'date': '2026-02-01',
                'concept': 'WHOLE FOODS',
                'amount': -55.00,
            },
            user=seth,
        )
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_account(self, client, alice):
        response = client.post(
            '/transactions/',
            json={'account_id': 9999, 'date': '2026-02-01', 'concept': 'X', 'amount': -1},
            user=alice,
        )
        assert response.status_code == 404
