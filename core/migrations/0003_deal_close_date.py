# Generated by Django 4.2.7 on 2023-11-09 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_purchase_delivery_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='close_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
