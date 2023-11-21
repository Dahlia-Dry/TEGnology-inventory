# Generated by Django 4.2.7 on 2023-11-17 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_invoice_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='IBAN',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='SWIFT_BIC',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='address',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='bank_account',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='bank_name',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='cvr',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='name',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='po_number',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='shipping_address',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[(1, 'deal closed'), (2, 'quotation sent'), (3, 'order confirmation sent'), (4, 'invoice sent'), (5, 'delivery scheduled'), (6, 'delivery confirmed')], default='deal closed', max_length=50),
        ),
    ]