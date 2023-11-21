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

def create_timestamp():
    try:
        t=Timestamp.objects.get(name='last_pipedrive_sync')
        t.delete()
    except:
        pass
    t=Timestamp.objecst.create(name='last_pipedrive_sync')
    t.save()

def create_tegnology():
    try:
        c = Customer.objects.get(name='TEGnology Aps')
        c.delete()
    except:
        pass
    tegnology=Customer.objects.create(name='TEGnology Aps',
                                    address= """TEGnology Aps <br /> Maskinvej 5 <br /> 2860 Søborg <br /> Denmark""",
                                    bank_account="54440240394",
                                    IBAN="DK7054440000240394",
                                    SWIFT_BIC="ALBADKKK",
                                    bank_name="Arbejdernes Landsbank",
                                    cvr="33370873",
                                    phone="+45 22837732",
                                    email="info@TEGnology.dk")
    tegnology.save()
    
def clear_dbs():
    order_records = Order.objects.all()
    for r in order_records:
        r.delete()
    product_records = Product.objects.all()
    for r in product_records:
        r.delete()
    purchase_records = Purchase.objects.all()
    for r in purchase_records:
        r.delete()
    invoice_records = Invoice.objects.all()
    for r in invoice_records:
        r.delete()

def load_pipedrive_history():
    """This function fetches all won orders from pipedrive and logs them as Order objects"""
    """databases should be emptied first"""
    clear_dbs()
    won_orders = client.deals.get_all_deals_with_filter(2)['data']
    for d in won_orders:
        print(f"creating order record for {d['title']}")
        customer_name = d['org_id']['name']
        try:
            person = d['person_id']['name']
        except:
            person=None
        try:
            email = d['person_id']['email'][0]['value']
        except:
            email=None
        try:
            customer_instance=Customer.objects.get(name=customer_name)
        except:
            customer_instance= Customer.objects.create(name=customer_name,
                                    address=d['org_id']['address'],
                                    )
        customer_instance.save()
        order_instance = Order.objects.create(name=d['title'],
                            pipedrive_id=d['id'],
                            status_date=datetime.datetime.strptime(d['update_time'],'%Y-%m-%d %H:%M:%S').date(),
                            close_date = datetime.datetime.strptime(d['close_time'],'%Y-%m-%d %H:%M:%S').date(),
                            pipedrive_meta=d,
                            total=d['weighted_value'],
                            currency=d['formatted_value'][0],
                            customer=customer_instance,
                            contact_person=person,
                            contact_email=email)
        print('saving order')
        order_instance.save()
        print(f"created order record for {d['title']}")

if __name__ == '__main__':
    create_timestamp()
    create_tegnology()
    load_pipedrive_history()
