# Generated by Django 4.2.7 on 2023-11-15 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='vat',
            field=models.FloatField(default=0, verbose_name='VAT (%)'),
        ),
    ]
