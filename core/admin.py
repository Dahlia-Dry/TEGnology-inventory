from django.contrib import admin

# Register your models here.
from .models import *
import os

class Product_admin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class Order_admin(admin.ModelAdmin):
    list_display = ['name','last_updated']
    search_fields = ['name']

class Purchase_admin(admin.ModelAdmin):
    list_display = ['order','status','order_date','product','quantity']
    search_fields = ['order','status','order_date','product','quantity']

class Entry_admin(admin.ModelAdmin):
    list_display = ['product','date','quantity','user']
    search_fields = ['product','date','quantity','user']


# Register your models here.
admin.site.register(Product,Product_admin)
admin.site.register(Order,Order_admin)
admin.site.register(Purchase,Purchase_admin)
admin.site.register(Entry,Entry_admin)