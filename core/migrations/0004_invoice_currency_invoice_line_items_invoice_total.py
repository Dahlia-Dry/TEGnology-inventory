# Generated by Django 4.2.7 on 2023-11-16 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_invoice_file_invoice_filepath_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='currency',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='line_items',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='total',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
