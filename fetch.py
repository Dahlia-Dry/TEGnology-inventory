import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')
django.setup()

from core.models import *
from decouple import config
from pipedrive.client import Client
import datetime
import uuid
import pdfkit
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

client = Client(domain=config('PIPEDRIVE_DOMAIN'))
client.set_api_token(config('PIPEDRIVE_API_TOKEN'))

def fetch_pipedrive_latest():
    t = Timestamp.objects.get(label='last_pipedrive_sync')
    params = {
    'since_timestamp': t.last_updated.strftime('%Y-%m-%d %H:%M:00'),
    }
    response = client.recents.get_recent_changes(params=params)
    new_deals = [item for item in response['data'] if item['item']=='deal' and item['data']['status']=='won']
    if len(new_deals) >0:
        return new_deals
    else:
        return None
 
