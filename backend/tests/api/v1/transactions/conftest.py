"""
tests/api/v1/transactions/conftest.py — Shared fixtures for transaction endpoint tests.

Fixtures provided here supplement the root conftest (alice, seth, household,
other_household, account_type, account, label, other_label, transaction,
labeled_transaction) with transaction-specific helpers used across multiple
HTTP-method test files.
"""

import hashlib

import pandas as pd
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from ninja.testing import TestClient

from api.v1.transactions import router
from transactions.models import Transaction


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


def make_tx(account, *, date, concept, amount, suffix=''):
    """Lightweight helper for bulk transaction creation in pagination/sorting tests."""
    unique = f'{account.id}|{date}|{concept}|{suffix}'
    dedupe_hash = hashlib.sha256(unique.encode()).hexdigest()
    return Transaction.objects.create(
        dedupe_hash=dedupe_hash,
        date=date,
        concept=concept,
        amount=amount,
        account=account,
    )
