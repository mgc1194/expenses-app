"""
tests/banking/test_models.py — Unit tests for banking-domain models.

Extracted from tests/transactions/test_models.py as part of the banking
app extraction. Bank, AccountType, and Account tests live here; Label and
Transaction tests remain in tests/transactions/test_models.py.
"""

import pytest
from django.db.models import ProtectedError
from django.db.utils import IntegrityError

from banking.constants import HandlerKeys
from banking.handlers.accounts import ACCOUNT_HANDLERS
from banking.models import Account, AccountType, Bank
from tests.factories import AccountFactory, HouseholdFactory

# ── Module-local fixtures ─────────────────────────────────────────────────────
# The shared conftest already provides: household, other_household, account_type,
# account, label, transaction. Only fixtures that are specific to model tests
# (e.g. "Smith Family" name, or second household) are defined below.


@pytest.fixture
def household(db):
    """Override the shared fixture to use the canonical Smith Family name."""
    return HouseholdFactory(name='Smith Family')


@pytest.fixture
def other_household(db):
    return HouseholdFactory(name='Jones Family')


# bank / account_type are system-seeded; use the shared conftest fixtures.
# account comes from conftest and depends on the local household.


# ── Bank ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestBank:
    def test_can_be_retrieved(self, bank):
        assert bank.pk is not None

    def test_string_representation(self, bank):
        assert str(bank) == 'SoFi'

    def test_name_must_be_unique(self, bank):
        with pytest.raises(IntegrityError):
            Bank.objects.create(name='SoFi')

    def test_logo_is_optional(self):
        bank = Bank.objects.create(name='Test Bank')
        assert not bank.logo

    def test_cannot_be_deleted_with_account_types(self):
        account_type = AccountType.objects.get(handler_key=HandlerKeys.SOFI_SAVINGS)
        with pytest.raises(ProtectedError):
            account_type.bank.delete()


# ── AccountType ─────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAccountType:
    def test_can_be_retrieved(self, account_type):
        assert account_type.pk is not None

    def test_string_representation(self, account_type):
        assert 'SoFi' in str(account_type)

    def test_handler_key_must_be_unique(self, account_type):
        with pytest.raises(IntegrityError):
            AccountType.objects.create(
                name='Duplicate',
                handler_key=account_type.handler_key,
                bank=account_type.bank,
            )

    def test_get_handler_returns_correct_handler(self, account_type):
        handler = account_type.get_handler()
        assert handler is ACCOUNT_HANDLERS[HandlerKeys.SOFI_SAVINGS]


# ── Account ───────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAccount:
    def test_can_be_created(self, account):
        assert account.pk is not None

    def test_string_representation(self, account):
        assert 'SoFi' in str(account)

    def test_belongs_to_a_household(self, account, household):
        assert account.household == household

    def test_handler_key_resolved_through_account_type(self, account):
        assert account.handler_key == account.account_type.handler_key

    def test_name_must_be_unique_per_household(self, account, account_type, household):
        with pytest.raises(IntegrityError):
            Account.objects.create(
                name=account.name,
                account_type=account_type,
                household=household,
            )

    def test_same_name_allowed_in_different_households(self, account_type, account):
        other_household = HouseholdFactory(name='Jones Family')
        other_account = AccountFactory(
            name=account.name,
            account_type=account_type,
            household=other_household,
        )
        assert other_account.pk is not None

    def test_two_accounts_of_same_type_allowed_in_household(self, account_type, household):
        AccountFactory(name='Account 360 Savings', account_type=account_type, household=household)
        AccountFactory(name="Partner's 360 Savings", account_type=account_type, household=household)
        assert Account.objects.filter(household=household).count() == 2

    def test_cannot_be_deleted_with_transactions(self, transaction):
        with pytest.raises(ProtectedError):
            transaction.account.delete()
