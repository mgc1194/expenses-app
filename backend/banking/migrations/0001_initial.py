"""
banking/migrations/0001_initial.py

Claims the existing banks, account_types, and accounts tables under the
banking app label. No new tables are created — this is a Django state
migration only.

SeparateDatabaseAndState is used throughout: database_operations is empty
(the tables already exist, created by transactions/migrations/0001_initial.py),
and state_operations describe the models so Django's ORM knows about them
under the banking label.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Bank',
                    fields=[
                        (
                            'id',
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name='ID',
                            ),
                        ),
                        ('name', models.CharField(max_length=255, unique=True)),
                        ('logo', models.ImageField(blank=True, null=True, upload_to='banks/')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={'db_table': 'banks'},
                ),
                migrations.CreateModel(
                    name='AccountType',
                    fields=[
                        (
                            'id',
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name='ID',
                            ),
                        ),
                        ('name', models.CharField(max_length=255)),
                        (
                            'handler_key',
                            models.CharField(
                                choices=[
                                    ('sofi-savings', 'SoFi Savings'),
                                    ('sofi-checking', 'SoFi Checking'),
                                    ('co-checking', '360 Checking'),
                                    ('co-savings', '360 Performance Savings'),
                                    ('co-quicksilver', 'Quicksilver Credit Card'),
                                    ('wf-checking', 'Checking'),
                                    ('wf-savings', 'Savings'),
                                    ('chase', 'Chase Card'),
                                    ('discover', 'Discover Card'),
                                    ('amex-delta', 'Delta SkyMiles Card'),
                                ],
                                max_length=255,
                                unique=True,
                            ),
                        ),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        (
                            'bank',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name='account_types',
                                to='banking.bank',
                            ),
                        ),
                    ],
                    options={
                        'db_table': 'account_types',
                        'unique_together': {('bank', 'name')},
                    },
                ),
                migrations.CreateModel(
                    name='Account',
                    fields=[
                        (
                            'id',
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name='ID',
                            ),
                        ),
                        ('name', models.CharField(max_length=255)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        (
                            'account_type',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name='accounts',
                                to='banking.accounttype',
                            ),
                        ),
                        (
                            'household',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name='accounts',
                                to='users.household',
                            ),
                        ),
                    ],
                    options={
                        'db_table': 'accounts',
                        'unique_together': {('household', 'name')},
                    },
                ),
            ],
        ),
    ]
