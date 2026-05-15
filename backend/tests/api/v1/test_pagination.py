"""
tests/api/v1/test_pagination.py — Tests for transaction list pagination and sorting.

IMPORTANT: Replace your existing test_pagination.py entirely with this file.
"""

import hashlib

import pytest
from ninja.testing import TestClient

from api.v1.transactions import router
from tests.factories import AccountFactory, LabelFactory, TransactionFactory
from transactions.models import Transaction

# ── Module-local fixtures ─────────────────────────────────────────────────────
# Shared conftest provides: alice, household, account_type.
# `account` is overridden here to ensure it is wired to alice's household.


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def account(db, account_type, household):
    """An account in alice's household — required for pagination queries to return results."""
    return AccountFactory(name='Pagination Account', account_type=account_type, household=household)


def _tx(account, *, date, concept, amount, suffix=''):
    """Lightweight helper for bulk transaction creation in pagination tests."""
    unique = f'{account.id}|{date}|{concept}|{suffix}'
    dedupe_hash = hashlib.sha256(unique.encode()).hexdigest()
    return Transaction.objects.create(
        dedupe_hash=dedupe_hash,
        date=date,
        concept=concept,
        amount=amount,
        account=account,
    )


@pytest.fixture
def fifty_five_transactions(db, account):
    """55 transactions each on a unique date for pagination testing."""
    from datetime import date, timedelta

    base = date(2026, 1, 1)
    return [
        _tx(account, date=base + timedelta(days=i), concept=f'TX {i}', amount=-float(i + 1))
        for i in range(55)
    ]


# ── Basic pagination ──────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestPagination:
    def test_default_page_size_is_20(self, client, alice, household, fifty_five_transactions):
        response = client.get(f'/transactions/?household_id={household.id}', user=alice)
        assert response.status_code == 200
        assert len(response.json()['results']) == 20

    def test_next_cursor_present_when_more_results(
        self, client, alice, household, fifty_five_transactions
    ):
        response = client.get(f'/transactions/?household_id={household.id}', user=alice)
        assert response.json()['next_cursor'] is not None

    def test_next_cursor_absent_on_last_page(
        self, client, alice, household, fifty_five_transactions
    ):
        # The forward-pagination query param is `cursor`, not `next_cursor`.
        # `next_cursor` is what the response returns; `cursor` is what you send.
        cursor = None
        for _ in range(10):  # safety ceiling: 10 * 20 > 55
            url = f'/transactions/?household_id={household.id}'
            if cursor:
                url += f'&cursor={cursor}'
            data = client.get(url, user=alice).json()
            cursor = data['next_cursor']
            if cursor is None:
                break
        else:
            pytest.fail('next_cursor never became None after exhausting all pages')
        assert data['next_cursor'] is None

    def test_full_forward_backward_traversal(
        self, client, alice, household, fifty_five_transactions
    ):
        forward_ids = []
        cursor = None
        data = None
        for _ in range(10):
            url = f'/transactions/?household_id={household.id}'
            if cursor:
                url += f'&cursor={cursor}'
            data = client.get(url, user=alice).json()
            forward_ids.extend(t['id'] for t in data['results'])
            cursor = data['next_cursor']
            if cursor is None:
                break
        else:
            pytest.fail('Forward traversal did not terminate within page limit')

        backward_ids = []
        prev = data['previous_cursor']
        for _ in range(10):
            if prev is None:
                break
            url = f'/transactions/?household_id={household.id}&previous_cursor={prev}'
            data = client.get(url, user=alice).json()
            backward_ids.extend(t['id'] for t in data['results'])
            prev = data['previous_cursor']

        assert len(set(forward_ids)) == 55
        assert len(backward_ids) == len(set(backward_ids))
        assert set(backward_ids).issubset(set(forward_ids))


# ── Nullable field sorting ────────────────────────────────────────────────────
# The endpoint coalesces null label names to '' for sorting.
# '' < any non-empty string, so ASC puts unlabelled rows FIRST,
# and DESC puts unlabelled rows LAST.


@pytest.mark.django_db
class TestNullableFieldSorting:
    @pytest.fixture
    def account_with_labels(self, db, household, account_type):
        acct = AccountFactory(
            name='Label Test Account', account_type=account_type, household=household
        )
        label_a = LabelFactory(name='AAA Label', color='#000000', household=household)
        label_z = LabelFactory(name='ZZZ Label', color='#ffffff', household=household)
        for i in range(3):
            TransactionFactory(
                account=acct,
                date='2026-01-01',
                concept=f'UNLABELLED {i}',
                amount=-10.00,
            )
        TransactionFactory(
            account=acct,
            date='2026-01-02',
            concept='AAA TX',
            amount=-20.00,
            label=label_a,
        )
        TransactionFactory(
            account=acct,
            date='2026-01-03',
            concept='ZZZ TX',
            amount=-30.00,
            label=label_z,
        )
        return acct

    def test_sort_by_label_asc_puts_nulls_first(
        self, client, alice, household, account_with_labels
    ):
        # ASC: '' < 'AAA Label' < 'ZZZ Label' — nulls sort first
        url = f'/transactions/?household_id={household.id}&sort=label&sort_dir=asc'
        response = client.get(url, user=alice)
        results = response.json()['results']
        names = [r['label_name'] for r in results]
        non_null = [n for n in names if n is not None]
        last_null_idx = max(i for i, n in enumerate(names) if n is None)
        first_label_idx = names.index(non_null[0])
        assert last_null_idx < first_label_idx
        assert non_null == sorted(non_null)

    def test_sort_by_label_desc_puts_nulls_last(
        self, client, alice, household, account_with_labels
    ):
        # DESC: 'ZZZ Label' > 'AAA Label' > '' — nulls sort last
        url = f'/transactions/?household_id={household.id}&sort=label&sort_dir=desc'
        response = client.get(url, user=alice)
        results = response.json()['results']
        names = [r['label_name'] for r in results]
        non_null = [n for n in names if n is not None]
        first_null_idx = next(i for i, n in enumerate(names) if n is None)
        last_label_idx = max(i for i, n in enumerate(names) if n is not None)
        assert last_label_idx < first_null_idx
        assert non_null == sorted(non_null, reverse=True)
