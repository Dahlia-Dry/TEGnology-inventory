# Generated by Django 4.2.7 on 2023-11-27 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_order_prev_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_notice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.deliverynotice'),
        ),
    ]