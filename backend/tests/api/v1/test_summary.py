"""
tests/api/v1/test_summary.py — Integration tests for GET /api/v1/summary/.

Note: this module defines its own bank/account_type fixtures because the
summary tests use a standalone fake bank ("Test Bank") to avoid coupling
to migration state. Everything else uses factories.
"""

import pytest
from django.test import Client

from tests.factories import AccountFactory, HouseholdFactory, LabelFactory, UserFactory
from transactions.models import AccountType, Bank, Transaction

# ── Module-local fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def household(db):
    return HouseholdFactory(name='Test Household')


@pytest.fixture
def other_household(db):
    return HouseholdFactory(name='Other Household')


@pytest.fixture
def user(db, household):
    u = UserFactory(email='test@example.com', username='test@example.com')
    u.set_password('Password1!')
    u.save()
    u.households.add(household)
    return u


@pytest.fixture
def other_user(db, other_household):
    u = UserFactory(email='other@example.com', username='other@example.com')
    u.set_password('Password1!')
    u.save()
    u.households.add(other_household)
    return u


@pytest.fixture
def bank(db):
    return Bank.objects.create(name='Test Bank')


@pytest.fixture
def account_type(db, bank):
    return AccountType.objects.create(
        name='Savings',
        handler_key='test_savings',
        bank=bank,
    )


@pytest.fixture
def account(db, account_type, household):
    return AccountFactory(name='Test Savings', account_type=account_type, household=household)


@pytest.fixture
def food_label(db, household):
    return LabelFactory(name='Groceries', color='#16a34a', category='Food', household=household)


@pytest.fixture
def income_label(db, household):
    return LabelFactory(name='Income', color='#036628', category='Income', household=household)


@pytest.fixture
def transport_label(db, household):
    return LabelFactory(name='Gas', color='#2563eb', category='Transport', household=household)


@pytest.fixture
def earnings_label(db, household):
    return LabelFactory(name='Paycheck', color='#059669', category='Earnings', household=household)


@pytest.fixture
def no_category_label(db, household):
    return LabelFactory(name='Miscellaneous', color='#6B7280', category='', household=household)


@pytest.fixture
def auth_client(db, user):
    client = Client()
    client.force_login(user)
    return client


def _tx(account, amount, label=None, date='2026-03-15', concept='TEST', suffix=''):
    """Lightweight helper for creating summary-test transactions."""
    return Transaction.objects.create(
        dedupe_hash=f'hash_{amount}_{label}_{date}_{suffix}',
        date=date,
        concept=concept,
        amount=amount,
        account=account,
        label=label,
    )


# ── Basic behaviour ───────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSummaryBasic:
    def test_returns_200_for_member(self, auth_client, household):
        response = auth_client.get(f'/api/v1/summary/?household_id={household.id}')
        assert response.status_code == 200

    def test_403_for_non_member(self, auth_client, other_household):
        response = auth_client.get(f'/api/v1/summary/?household_id={other_household.id}')
        assert response.status_code == 403

    def test_404_for_missing_household(self, auth_client):
        response = auth_client.get('/api/v1/summary/?household_id=99999')
        assert response.status_code == 404

    def test_401_for_unauthenticated(self, household):
        response = Client().get(f'/api/v1/summary/?household_id={household.id}')
        assert response.status_code == 401

    def test_empty_household_returns_zero_totals(self, auth_client, household):
        data = auth_client.get(f'/api/v1/summary/?household_id={household.id}').json()
        assert data['total'] == 0.0
        assert data['balance'] == 0.0
        assert data['uncategorised_total'] == 0.0
        assert data['earnings'] == []
        assert data['spending'] == []

    def test_400_for_invalid_month(self, auth_client, household):
        response = auth_client.get(f'/api/v1/summary/?household_id={household.id}&month=bad')
        assert response.status_code == 400

    def test_400_for_month_with_invalid_number(self, auth_client, household):
        response = auth_client.get(f'/api/v1/summary/?household_id={household.id}&month=2026-13')
        assert response.status_code == 400


# ── Aggregation ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSummaryAggregation:
    def test_spending_label_appears_in_spending(self, auth_client, account, household, food_label):
        _tx(account, -42.57, food_label)
        data = auth_client.get(f'/api/v1/summary/?household_id={household.id}').json()
        assert len(data['spending']) == 1
        assert data['spending'][0]['category'] == 'Food'
        assert data['spending'][0]['labels'][0]['label_name'] == 'Groceries'

    def test_earnings_label_appears_in_earnings(
        self, auth_client, account, household, earnings_label
    ):
        _tx(account, 2500.00, earnings_label)
        data = auth_client.get(f'/api/v1/summary/?household_id={household.id}').json()
        assert len(data['earnings']) == 1
        assert data['earnings'][0]['category'] == 'Earnings'

    def test_unlabelled_transaction_goes_to_uncategorised(self, auth_client, account, household):
        _tx(account, -15.00)
        data = auth_client.get(f'/api/v1/summary/?household_id={household.id}').json()
        assert data['uncategorised_total'] == pytest.approx(-15.00)

    def test_total_is_sum_of_all_spending(
        self, auth_client, account, household, food_label, transport_label
    ):
        _tx(account, -42.57, food_label, suffix='1')
        _tx(account, -20.00, transport_label, suffix='2')
        data = auth_client.get(f'/api/v1/summary/?household_id={household.id}').json()
        assert data['total'] == pytest.approx(-62.57)

    def test_income_label_excluded_from_spending_total(
        self, auth_client, account, household, income_label
    ):
        _tx(account, 1000.00, income_label)
        data = auth_client.get(f'/api/v1/summary/?household_id={household.id}').json()
        assert data['spending'] == []
        assert data['total'] == pytest.approx(1000.00)

    def test_other_household_transactions_not_included(
        self, auth_client, other_household, household, account_type, food_label
    ):
        other_account = AccountFactory(
            name='Other Account', account_type=account_type, household=other_household
        )
        other_label = LabelFactory(name='Groceries', category='Food', household=other_household)
        _tx(other_account, -100.00, other_label)
        data = auth_client.get(f'/api/v1/summary/?household_id={household.id}').json()
        assert data['total'] == 0.0

    def test_month_filter_excludes_other_months(self, auth_client, account, household, food_label):
        _tx(account, -10.00, food_label, date='2026-02-15', suffix='feb')
        _tx(account, -20.00, food_label, date='2026-03-15', suffix='mar')
        data = auth_client.get(f'/api/v1/summary/?household_id={household.id}&month=2026-03').json()
        assert data['total'] == pytest.approx(-20.00)
