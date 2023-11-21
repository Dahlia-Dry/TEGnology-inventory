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
        purchase_instance= Purchase.objects.create(order=order_instance,
                                                   status=order_instance.status,
                                                    product=product_instance,
                                                    quantity=p['quantity'],
                                                    unit_price=p['item_price'])
        purchase_instance.save()
        i+=1
        print(f"created purchase record for {p['name']}-{p['quantity']}")

@receiver(post_save, sender=Order)
def update_order_products(sender,instance,created,**kwargs):
    if created:
        return
    log_purchases(instance)
