"""
tests/factories/transactions.py — Factories for Bank, AccountType, Account, Label, Transaction.

Design notes
------------
Bank and AccountType are *system-defined* records that are seeded via data
migrations (e.g. the "SoFi" bank and "sofi-savings" account type always
exist in the test database).  To avoid IntegrityError on their unique
constraints we use ``django_get_or_create`` — factories will find the
existing seed row instead of trying to INSERT a duplicate.

Account, Label, and Transaction are *user-owned* records that must be
created fresh for each test.  Their factories use normal INSERT semantics.
"""

import secrets
from datetime import date

import factory

from transactions.constants import HandlerKeys
from transactions.models import Account, AccountType, Bank, Label, Transaction

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
    # will find it without touching these fields.  They are supplied here so
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


# ── Label ─────────────────────────────────────────────────────────────────────


class LabelFactory(factory.django.DjangoModelFactory):
    """
    Creates a Label within a generated Household.

    Label names are unique per household; the Sequence guarantees no
    collisions when multiple labels are created for the same household.
    Override for named labels:
        LabelFactory(name='Groceries', household=my_household)
    """

    class Meta:
        model = Label

    name = factory.Sequence(lambda n: f'Label {n}')
    color = '#6B7280'
    category = ''
    household = factory.SubFactory(HouseholdFactory)


# ── Transaction ───────────────────────────────────────────────────────────────


class TransactionFactory(factory.django.DjangoModelFactory):
    """
    Creates a Transaction linked to a generated Account.

    The dedupe_hash is a random 64-hex string so parallel tests never
    collide on the (account, dedupe_hash) unique constraint.

    Common overrides:
        TransactionFactory(account=my_account, amount=-99.99, date=date(2026, 3, 1))
        TransactionFactory(label=my_label)
    """

    class Meta:
        model = Transaction

    dedupe_hash = factory.LazyFunction(lambda: secrets.token_hex(32))  # 64 hex chars
    date = factory.LazyFunction(date.today)
    concept = factory.Sequence(lambda n: f'TRANSACTION {n}')
    amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=False)
    source = Transaction.Source.IMPORT
    raw_data = None
    account = factory.SubFactory(AccountFactory)
    label = None
