"""
transactions/migrations/0008_account_fk_to_banking.py

Updates Django's migration state so Transaction.account points to
banking.Account instead of transactions.Account.

SeparateDatabaseAndState is used: the physical foreign key column already
points to the correct rows in the accounts table. No ALTER TABLE is
needed — only Django's internal state needs updating.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('banking', '0001_initial'),
        ('transactions', '0007_transaction_idx_transactions_cursor'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='transaction',
                    name='account',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='transactions',
                        to='banking.account',
                    ),
                ),
            ],
        ),
    ]
