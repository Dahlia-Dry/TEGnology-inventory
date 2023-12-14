# Generated by Django 4.2.7 on 2023-12-04 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_remove_deliverynotice_currency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='prev_status',
            field=models.IntegerField(choices=[(0, 'Deal Pending'), (1, 'Quotation Sent'), (2, 'Purchase Order Received'), (3, 'Order Confirmation Sent'), (4, 'Invoice Sent'), (5, 'Delivery Scheduled'), (6, 'Delivery Confirmed')], default=1),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, 'Deal Pending'), (1, 'Quotation Sent'), (2, 'Purchase Order Received'), (3, 'Order Confirmation Sent'), (4, 'Invoice Sent'), (5, 'Delivery Scheduled'), (6, 'Delivery Confirmed')], default=1),
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]