# Generated by Django 4.2.7 on 2023-11-10 11:10

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_purchase_purchase_number'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Stock',
            new_name='Entry',
        ),
    ]
