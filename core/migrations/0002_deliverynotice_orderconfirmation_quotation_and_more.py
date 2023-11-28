# Generated by Django 4.2.7 on 2023-11-23 10:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryNotice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filepath', models.FilePathField()),
                ('sent_date', models.DateField(blank=True, null=True, verbose_name='sent date')),
                ('created_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filepath', models.FilePathField()),
                ('sent_date', models.DateField(blank=True, null=True, verbose_name='sent date')),
                ('created_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filepath', models.FilePathField()),
                ('sent_date', models.DateField(blank=True, null=True, verbose_name='sent date')),
                ('created_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_notice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.deliverynotice'),
        ),
        migrations.AddField(
            model_name='order',
            name='order_confirmation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.orderconfirmation'),
        ),
        migrations.AddField(
            model_name='order',
            name='quotation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.quotation'),
        ),
    ]