# Generated by Django 4.2.7 on 2023-11-21 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_purchase_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='last_updated',
        ),
        migrations.AddField(
            model_name='order',
            name='status_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]