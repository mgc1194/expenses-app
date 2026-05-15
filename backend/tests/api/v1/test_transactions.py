"""
tests/api/v1/test_transactions.py — Tests for transaction management endpoints.
"""

from unittest.mock import Mock

import pandas as pd
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from ninja.testing import TestClient

from api.v1.transactions import router
from tests.factories import TransactionFactory
from transactions.models import Transaction

# ── Module-local fixtures ─────────────────────────────────────────────────────
# Shared conftest provides: alice, seth, household, other_household,
# account_type, account, label, other_label, transaction, labeled_transaction.


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def csv_file():
    return SimpleUploadedFile(
        'test.csv',
        b'Date,Description,Amount\n2026-01-15,TRADER JOES,-45.50\n',
        content_type='text/csv',
    )


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        [
            {
                'dedupe_hash': 'abc123' * 10 + 'abcd',
                'Date': pd.Timestamp('2026-01-15'),
                'Concept': 'TRADER JOES',
                'Amount': -45.50,
            }
        ]
    )


# ── GET /transactions/ ────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestListTransactions:
    def test_returns_transactions_for_household(self, client, alice, transaction, household):
        response = client.get(f'/transactions/?household_id={household.id}', user=alice)
        assert response.status_code == 200
        data = response.json()['results']
        assert len(data) == 1
        assert data[0]['id'] == transaction.id

    def test_returns_empty_for_household_with_no_transactions(self, client, alice, household):
        response = client.get(f'/transactions/?household_id={household.id}', user=alice)
        assert response.status_code == 200
        assert response.json()['results'] == []

    def test_includes_label_fields_when_present(
        self, client, alice, labeled_transaction, label, household
    ):
        response = client.get(f'/transactions/?household_id={household.id}', user=alice)
        data = response.json()['results'][0]
        assert data['label_id'] == label.id
        assert data['label_name'] == label.name
        assert data['label_color'] == label.color

    def test_results_ordered_by_date_descending(self, client, alice, account, household):
        TransactionFactory(
            account=account,
            date='2026-01-01',
            concept='OLDER',
            amount=-10.00,
        )
        TransactionFactory(
            account=account,
            date='2026-01-15',
            concept='NEWER',
            amount=-20.00,
        )

        response = client.get(f'/transactions/?household_id={household.id}', user=alice)
        data = response.json()['results']
        assert data[0]['concept'] == 'NEWER'
        assert data[1]['concept'] == 'OLDER'

    def test_unauthenticated_returns_401(self, client, household):
        response = client.get(f'/transactions/?household_id={household.id}')
        assert response.status_code == 401

    def test_returns_403_for_non_member(self, client, seth, household):
        response = client.get(f'/transactions/?household_id={household.id}', user=seth)
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_household(self, client, alice):
        response = client.get('/transactions/?household_id=9999', user=alice)
        assert response.status_code == 404


# ── POST /transactions/ ───────────────────────────────────────────────────────


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


# ── PATCH /transactions/{id}/ ─────────────────────────────────────────────────


@pytest.mark.django_db
class TestUpdateTransaction:
    def test_updates_concept(self, client, alice, transaction):
        response = client.patch(
            f'/transactions/{transaction.id}/',
            json={'concept': 'UPDATED CONCEPT'},
            user=alice,
        )
        assert response.status_code == 200
        assert response.json()['concept'] == 'UPDATED CONCEPT'

    def test_assigns_label(self, client, alice, transaction, label):
        response = client.patch(
            f'/transactions/{transaction.id}/',
            json={'label_id': label.id},
            user=alice,
        )
        assert response.status_code == 200
        assert response.json()['label_id'] == label.id

    def test_clears_label_when_null(self, client, alice, labeled_transaction):
        response = client.patch(
            f'/transactions/{labeled_transaction.id}/',
            json={'label_id': None},
            user=alice,
        )
        assert response.status_code == 200
        assert response.json()['label_id'] is None

    def test_rejects_label_from_other_household(self, client, alice, transaction, other_label):
        response = client.patch(
            f'/transactions/{transaction.id}/',
            json={'label_id': other_label.id},
            user=alice,
        )
        assert response.status_code == 400

    def test_returns_400_when_no_fields_provided(self, client, alice, transaction):
        response = client.patch(f'/transactions/{transaction.id}/', json={}, user=alice)
        assert response.status_code == 400

    def test_returns_403_for_non_member(self, client, seth, transaction):
        response = client.patch(
            f'/transactions/{transaction.id}/',
            json={'concept': 'X'},
            user=seth,
        )
        assert response.status_code == 403

    def test_returns_404_for_nonexistent_transaction(self, client, alice):
        response = client.patch('/transactions/9999/', json={'concept': 'X'}, user=alice)
        assert response.status_code == 404


# ── DELETE /transactions/{id}/ ────────────────────────────────────────────────


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


# ── POST /transactions/import/ ────────────────────────────────────────────────


@pytest.mark.django_db
class TestImportTransactions:
    def test_import_returns_200(self, client, alice, account, csv_file, monkeypatch):
        mock_handler = Mock()
        mock_handler.process.return_value = pd.DataFrame(
            [
                {
                    'dedupe_hash': 'import' * 10 + 'abcd',
                    'raw_data': '{}',
                    'Date': pd.Timestamp('2026-01-15'),
                    'Concept': 'TRADER JOES',
                    'Amount': -45.50,
                }
            ]
        )
        monkeypatch.setattr(
            'api.v1.transactions.upsert_transactions',
            lambda df, acc: {'inserted': 1, 'skipped': 0, 'total': 1},
        )
        # The endpoint resolves the handler via ACCOUNT_HANDLERS[account.handler_key]
        monkeypatch.setitem(
            __import__('api.v1.transactions', fromlist=['ACCOUNT_HANDLERS']).ACCOUNT_HANDLERS,
            account.handler_key,
            mock_handler,
        )
        response = client.post(
            f'/transactions/import?account_id={account.id}',
            FILES={'file': csv_file},
            user=alice,
        )
        assert response.status_code == 200
