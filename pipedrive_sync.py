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

client = Client(domain=config('PIPEDRIVE_DOMAIN'))
client.set_api_token(config('PIPEDRIVE_API_TOKEN'))

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

def load_pipedrive_history():
    """This function fetches all won orders from pipedrive and logs them as Order objects"""
    order_records = Order.objects.all()
    for r in order_records:
        r.delete()
    product_records = Product.objects.all()
    for r in product_records:
        r.delete()
    purchase_records = Purchase.objects.all()
    for r in purchase_records:
        r.delete()
    won_orders = client.deals.get_all_deals_with_filter(2)['data']
    for d in won_orders:
        order_instance = Order.objects.create(name=d['title'],
                            pipedrive_id=d['id'],
                            last_updated=datetime.datetime.strptime(d['update_time'],'%Y-%m-%d %H:%M:%S').date(),
                            close_date = datetime.datetime.strptime(d['close_time'],'%Y-%m-%d %H:%M:%S').date(),
                            pipedrive_meta=d,
                            order_number=  str(uuid.uuid4()))
        order_instance.save()
        print(f"created order record for {d['title']}")
        products= client.deals.get_deal_products(d['id'])['data']
        if products is None:
            continue
        i=1
        for p in products:
            try:
                product_instance = Product.objects.get(pipedrive_id=p['product_id'])
            except:
                product_instance = Product.objects.create(pipedrive_id=p['product_id'],
                                                          name=p['name'])
                product_instance.save()
                print(f"created product {p['name']}")
            purchase_instance= Purchase.objects.create(order=order_instance,
                                                       product=product_instance,
                                                       purchase_number=order_instance.order_number+'-'+str(i).zfill(2),
                                                       status='pending',
                                                       quantity=p['quantity'],
                                                       unit_price=p['item_price'],
                                                       currency=p['currency'],
                                                       order_date=datetime.datetime.strptime(p['add_time'],'%Y-%m-%d %H:%M:%S').date())
            purchase_instance.save()
            i+=1
            print(f"created purchase record for {p['name']}-{p['quantity']}-{str(purchase_instance.order_date)}")
        #create invoice
        line_items = Purchase.objects.filter(order=order_instance)
        invoice_context={'order_number':'1209123','logo_path':os.path.abspath('core/static/assets/logo.png')}
        n = str(uuid.uuid4())
        invoice_filepath = os.path.abspath(f'core/static/assets/invoices/{order_instance.name}.pdf')
        invoice_instance = Invoice.objects.create(invoice_number=n,
                                                  order=order_instance,
                                                  invoice_file=invoice_filepath)
        output_text=render_to_string('documents/invoice.html',invoice_context)
        pdfkit.from_string(output_text,invoice_filepath,options={"enable-local-file-access": ""})
        invoice_instance.save()

if __name__ == '__main__':
    #clear_dbs()
    load_pipedrive_history()
