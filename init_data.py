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
        t=Timestamp.objects.get(label='last_pipedrive_sync')
        t.delete()
    except:
        pass
    t=Timestamp.objects.create(label='last_pipedrive_sync')
    t.save()

def init_media():
    os.system('rm -rf media')
    os.system('mkdir media')
    os.system('mkdir media/order_confirmations')
    os.system('mkdir media/invoices')
    os.system('mkdir media/purchase_orders')
    os.system('mkdir media/quotations')

def create_tegnology():
    try:
        c = Customer.objects.get(name='TEGnology Aps')
        c.delete()
    except:
        pass
    tegnology=Customer.objects.create(name='TEGnology Aps',
                                    address= """TEGnology Aps <br /> Maskinvej 5 <br /> 2860 Søborg <br /> Denmark""",
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

def add_orders_to_db(queryset,status):
    for d in queryset:
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
        try:
            close_date= datetime.datetime.strptime(d['close_time'],'%Y-%m-%d %H:%M:%S').date()
        except Exception as e:
            close_date=None
        order_instance = Order.objects.create(name=d['title'],
                                            status=status,
                            pipedrive_id=d['id'],
                            status_date=datetime.datetime.strptime(d['update_time'],'%Y-%m-%d %H:%M:%S').date(),
                            close_date = close_date,
                            pipedrive_meta=d,
                            total=str(d['weighted_value']),
                            currency=d['formatted_value'][0],
                            customer=customer_instance,
                            contact_person=person,
                            contact_email=email)
        print('saving order')
        order_instance.save()
        print(f"created order record for {d['title']}")


def load_pipedrive_history():
    """This function fetches all won orders from pipedrive and logs them as Order objects"""
    """databases should be emptied first"""
    clear_dbs()
    won_orders = client.deals.get_all_deals_with_filter(2)['data']
    open_orders = client.deals.get_all_deals_with_filter(38)['data']
    add_orders_to_db(won_orders,1)
    add_orders_to_db(open_orders,0)

if __name__ == '__main__':
    init_media()
    create_timestamp()
    create_tegnology()
    load_pipedrive_history()