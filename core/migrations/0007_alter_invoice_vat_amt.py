# Generated by Django 4.2.7 on 2023-11-28 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_invoice_vat_amt_alter_invoice_vat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='vat_amt',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
