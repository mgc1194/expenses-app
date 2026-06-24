"""
tests/factories/banking.py — Factories for Bank, AccountType, Account.

Extracted from tests/factories/transactions.py as part of the banking app
extraction. Label and Transaction factories remain in transactions.py.

Design notes
------------
Bank and AccountType are *system-defined* records that are seeded via data
migrations (e.g. the "SoFi" bank and "sofi-savings" account type always
exist in the test database). To avoid IntegrityError on their unique
constraints we use ``django_get_or_create`` — factories will find the
existing seed row instead of trying to INSERT a duplicate.

Account is a *user-owned* record that must be created fresh for each test.
Its factory uses normal INSERT semantics.
"""

import factory

from banking.constants import HandlerKeys
from banking.models import Account, AccountType, Bank

from .users import HouseholdFactory

# ── Bank ──────────────────────────────────────────────────────────────────────


class BankFactory(factory.django.DjangoModelFactory):
    """
    Returns the seeded SoFi bank by default.

    Override ``name`` to get a different bank (it will be created if absent):
        BankFactory(name='Chase')
    """

    class Meta:
        model = Bank
        django_get_or_create = ('name',)

    name = 'SoFi'


# ── AccountType ───────────────────────────────────────────────────────────────


class AccountTypeFactory(factory.django.DjangoModelFactory):
    """
    Returns the seeded SoFi Savings account type by default.

    Override ``handler_key`` to pick a different seeded type:
        AccountTypeFactory(handler_key=HandlerKeys.SOFI_CHECKING)
    """

    class Meta:
        model = AccountType
        django_get_or_create = ('handler_key',)

    handler_key = HandlerKeys.SOFI_SAVINGS
    # name and bank are already set on the seeded row; django_get_or_create
    # will find it without touching these fields. They are supplied here so
    # that the factory can also CREATE a new AccountType in tests that need
    # an arbitrary one (e.g. test_utils.py).
    name = factory.LazyAttribute(lambda o: f'Account Type {o.handler_key}')
    bank = factory.SubFactory(BankFactory)


# ── Account ───────────────────────────────────────────────────────────────────


class AccountFactory(factory.django.DjangoModelFactory):
    """
    Creates a user-owned Account belonging to a generated Household.

    The account_type defaults to the seeded SoFi Savings type.
    Override for a different type:
        AccountFactory(account_type=AccountTypeFactory(handler_key=HandlerKeys.CO_CHECKING))
    """

    class Meta:
        model = Account

    name = factory.Sequence(lambda n: f'Test Account {n}')
    account_type = factory.SubFactory(AccountTypeFactory)
    household = factory.SubFactory(HouseholdFactory)
