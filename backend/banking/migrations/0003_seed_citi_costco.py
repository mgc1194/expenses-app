from django.db import migrations
from django.utils import timezone


def seed_citi_costco(apps, schema_editor):
    Bank = apps.get_model('banking', 'Bank')
    AccountType = apps.get_model('banking', 'AccountType')

    now = timezone.now()

    bank, _ = Bank.objects.update_or_create(
        name='Citi',
        defaults={
            'logo': 'banks/citi.png',
            'updated_at': now,
        },
    )

    AccountType.objects.update_or_create(
        handler_key='citi-costco',
        defaults={
            'name': 'Costco Anywhere Visa Card',
            'bank': bank,
            'updated_at': now,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('banking', '0002_add_citi_costco_handler'),
    ]

    operations = [
        migrations.RunPython(seed_citi_costco, migrations.RunPython.noop),
    ]
