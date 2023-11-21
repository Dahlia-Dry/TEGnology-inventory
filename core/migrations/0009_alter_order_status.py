# Generated by Django 4.2.7 on 2023-11-20 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'Deal Closed'), (2, 'Quotation Sent'), (3, 'Order Confirmation Sent'), (4, 'Invoice Sent'), (5, 'Delivery Scheduled'), (6, 'Delivery Confirmed')], default=1),
        ),
    ]