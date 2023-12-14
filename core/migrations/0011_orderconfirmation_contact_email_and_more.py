# Generated by Django 4.2.7 on 2023-11-29 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_invoice_sender_email_quotation_sender_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderconfirmation',
            name='contact_email',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='orderconfirmation',
            name='contact_person',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='orderconfirmation',
            name='currency',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='orderconfirmation',
            name='line_items',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderconfirmation',
            name='sender_email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='orderconfirmation',
            name='total',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='orderconfirmation',
            name='total_vat',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='orderconfirmation',
            name='vat',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='VAT (%)'),
        ),
        migrations.AddField(
            model_name='orderconfirmation',
            name='vat_amt',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('po_number', models.CharField(max_length=20, null=True)),
                ('po_file', models.FileField(upload_to='')),
                ('received_date', models.DateField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.order')),
            ],
        ),
    ]