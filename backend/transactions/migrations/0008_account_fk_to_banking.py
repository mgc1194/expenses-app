"""
transactions/migrations/0008_account_fk_to_banking.py

Completes the move of Bank, AccountType, and Account out of the
transactions app's migration state and into banking.

Two things happen here, both state-only (no ALTER/DROP/CREATE TABLE is
issued against the database):

1. Transaction.account is re-pointed to banking.Account.
2. Bank, AccountType, and Account are removed from the transactions app's
   migration state via DeleteModel. Without this step those three models
   would exist in BOTH transactions' state (created in
   transactions/migrations/0001_initial.py) and banking's state (created
   in banking/migrations/0001_initial.py) simultaneously. A future
   makemigrations run would then detect that transactions "has" models
   with no corresponding code and propose deleting them — which, if not
   caught and made state-only, would emit a real DROP TABLE against
   banks/account_types/accounts. The DeleteModel operations below close
   that gap by removing the duplicate state from transactions; the
   physical tables are untouched and already claimed under the banking
   app label by banking/migrations/0001_initial.py.
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
                # Remove banking-domain models from the transactions app state;
                # the underlying tables remain and are claimed by banking/0001_initial.
                migrations.DeleteModel(name='Account'),
                migrations.DeleteModel(name='AccountType'),
                migrations.DeleteModel(name='Bank'),
            ],
        ),
    ]
