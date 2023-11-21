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
               path('orders/id=<str:pk>',views.orders,name='orders_selected'),
               path('inventory',views.inventory,name='inventory'),
               path('profile',views.profile,name='profile'),
                path('profile/change-password',views.change_password,name='change_password'),
               path('inventory/<str:pk>/edit',views.edit_entry,name='edit_entry'),
               path('customers/<str:pk>/edit',views.edit_customer,name='edit_customer'),
               path('orders/id=<str:pk>/edit_meta',views.edit_order_meta,name='edit_order_meta'),
               path('orders/id=<str:pk>/edit_status',views.edit_order_status,name='edit_order_status'),
               path('orders/id=<str:pk>/<str:filetype>',views.view_file,name='view_file'),
               path('orders/id=<str:pk>/<str:filetype>/generate',views.gen_file,name='gen_file')
               ]