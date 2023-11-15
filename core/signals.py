from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
import os
from .models import *
from decouple import config
from pipedrive.client import Client
from django.conf import settings
from django.template.loader import render_to_string
import pdfkit

client = Client(domain=config('PIPEDRIVE_DOMAIN'))
client.set_api_token(config('PIPEDRIVE_API_TOKEN'))

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

def log_purchases(order_instance):
    print(f'running log order products for {order_instance.name}')
    #delete any existing old records
    old_records = Purchase.objects.filter(order=order_instance)
    for r in old_records:
        r.delete()
    products= client.deals.get_deal_products(order_instance.pipedrive_id)['data']
    if products is None:
        return
    i=1
    for p in products:
        try:
            product_instance = Product.objects.get(pipedrive_id=p['product_id'])
        except:
            product_instance = Product.objects.create(pipedrive_id=p['product_id'],
                                                        name=p['name'])
            product_instance.save()
            print(f"created product {p['name']}")
        if order_instance.order_number is None:
            order_number = ''
        else:
            order_number= order_instance.order_number
        purchase_instance= Purchase.objects.create(order=order_instance,
                                                    product=product_instance,
                                                    purchase_number=order_number+'-'+str(i).zfill(2),
                                                    status='pending',
                                                    quantity=p['quantity'],
                                                    unit_price=p['item_price'],
                                                    currency=p['currency'],
                                                    order_date=datetime.datetime.strptime(p['add_time'],'%Y-%m-%d %H:%M:%S').date())
        purchase_instance.save()
        i+=1
        print(f"created purchase record for {p['name']}-{p['quantity']}-{str(purchase_instance.order_date)}")

def create_invoice(order_instance):
    #delete old instance
    try:
        old_instance = Invoice.objects.get(order=order_instance)
        os.system(f'rm {old_instance.invoice_filepath}')
        old_instance.delete()
    except:
        pass
    #create invoice
    purchases = Purchase.objects.filter(order=order_instance)
    line_items = []
    for p in purchases:
        item = {}
        item['name'] = p.product.name
        item['quantity'] = p.quantity
        item['price'] = p.currency+f' {(p.quantity*p.unit_price):.2f}'
        line_items.append(item)
    invoice_context={'logo_path':os.path.join(settings.STATIC_ROOT,'assets/logo.png'),
                     'line_items':line_items}
    invoice_filepath = os.path.join(settings.STATIC_ROOT,f'assets/invoices/invoice-{order_instance.pipedrive_id}.pdf')
    try:
        person = order_instance.pipedrive_meta['person_id']['name']
    except:
        person=None
    try:
        email = order_instance.pipedrive_meta['person_id']['email'][0]['value']
    except:
        email=None
    invoice_instance = Invoice.objects.create(order=order_instance,
                                              created_date=order_instance.close_date,
                                              contact_person = person,
                                              contact_email=email,
                                              invoice_file=invoice_filepath)
    invoice_context['invoice'] = invoice_instance
    invoice_context['tegnology'] = Customer.objects.get(name='TEGnology Aps')
    output_text=render_to_string('documents/invoice.html',invoice_context)
    pdfkit.from_string(output_text,invoice_filepath,options={"enable-local-file-access": ""})
    invoice_instance.save()

@receiver(post_save, sender=Order)
def update_order_products(sender,instance,created,**kwargs):
    if created:
        return
    log_purchases(instance)
    create_invoice(instance)