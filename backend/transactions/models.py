"""
transactions/models.py — Bank, Account, and Transaction models.
"""

from django.db import models
from users.models import Household


class Bank(models.Model):
    """
    Represents a financial institution.
    handler_key maps to a key in ACCOUNT_HANDLERS in handlers/accounts.py.
    """
    name        = models.CharField(max_length=255)
    logo        = models.ImageField(upload_to='banks/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'banks'


class Account(models.Model):
    """
    Represents a specific financial account (e.g. SoFi Savings).
    Belongs to one Bank and one Household.
    handler_key maps to ACCOUNT_HANDLERS for CSV parsing.
    """
    name        = models.CharField(max_length=255)
    handler_key = models.CharField(max_length=255)
    bank        = models.ForeignKey(Bank, on_delete=models.PROTECT, related_name='accounts')
    household   = models.ForeignKey(Household, on_delete=models.PROTECT, related_name='accounts')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.bank.name} — {self.name}'

    class Meta:
        db_table = 'accounts'


class Transaction(models.Model):
    """
    Represents a single financial transaction.
    ID is an MD5 hash of the raw CSV row — generated before cleaning
    so that fields like balance disambiguate otherwise identical rows.
    Labels and category are manually assigned and never overwritten on re-import.
    """
    id                = models.CharField(max_length=32, primary_key=True)
    date              = models.DateField()
    concept           = models.TextField()
    amount            = models.DecimalField(max_digits=12, decimal_places=2)
    label             = models.CharField(max_length=255, blank=True, null=True)
    category          = models.CharField(max_length=255, blank=True, null=True)
    additional_labels = models.TextField(blank=True, null=True)
    account           = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    imported_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.date} — {self.concept} ({self.amount})'

    class Meta:
        db_table    = 'transactions'
        indexes     = [
            models.Index(fields=['date'],     name='idx_transactions_date'),
            models.Index(fields=['label'],    name='idx_transactions_label'),
            models.Index(fields=['category'], name='idx_transactions_category'),
        ]