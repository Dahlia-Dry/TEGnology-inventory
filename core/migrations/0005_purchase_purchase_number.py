# Generated by Django 4.2.7 on 2023-11-09 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_invoice_order_rename_inventory_stock_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='purchase_number',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
    ]
