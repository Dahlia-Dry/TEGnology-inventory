# Generated by Django 4.2.7 on 2023-12-11 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_order_prev_status_alter_order_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total_vat',
        ),
        migrations.RemoveField(
            model_name='order',
            name='vat_amt',
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
