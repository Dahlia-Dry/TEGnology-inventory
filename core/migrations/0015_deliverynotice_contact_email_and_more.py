# Generated by Django 4.2.7 on 2023-11-29 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_order_prev_status_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverynotice',
            name='contact_email',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='deliverynotice',
            name='contact_person',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='deliverynotice',
            name='currency',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='deliverynotice',
            name='delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='deliverynotice',
            name='line_items',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='deliverynotice',
            name='message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='deliverynotice',
            name='order_number',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='deliverynotice',
            name='sender_email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='deliverynotice',
            name='total',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
