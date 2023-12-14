from django.urls import path,re_path
import json
import copy
from core.models import *
from django.conf import settings
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('assets/favicon.ico'))),
               path('',views.dashboard,name='dashboard'),
               path('orders',views.orders,name='orders'),
               path('inventory',views.inventory,name='inventory'),
               path('inventory/<str:pk>/edit',views.edit_entry,name='edit_entry'),
               path('profile',views.profile,name='profile'),
               path('profile/change-password',views.change_password,name='change_password'),
               path('customers',views.customers,name='customers'),
               path('customers/<str:pk>/edit',views.edit_customer,name='edit_customer'),
               path('deals',views.deals,name='deals'),
               path('deals/<str:pk>',views.deal_detail,name='deal_detail'),
               path('orders/<str:pk>',views.order_detail,name='order_detail'),
               path('orders/<str:pk>/edit_meta',views.edit_order_meta,name='edit_order_meta'),
               path('orders/<str:pk>/edit_status',views.edit_order_status,name='edit_order_status'),
               path('orders/<str:pk>/send-<str:filetype>',views.mark_sent,name='mark_sent'),
               path('orders/<str:pk>/<str:filetype>',views.view_file,name='view_file'),
               path('orders/<str:pk>/<str:filetype>/generate',views.gen_file,name='gen_file'),
               path('orders/<str:pk>/<str:filetype>/upload',views.upload_file,name='upload_file')
               ]