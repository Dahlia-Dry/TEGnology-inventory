# Generated by Django 4.2.7 on 2023-11-10 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_rename_stock_entry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='purchase_number',
        ),
    ]
