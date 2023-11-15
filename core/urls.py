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
               path('edit/<str:pk>',views.edit_entry,name='edit_entry'),
               path('edit_customer',views.edit_customer,name='edit_customer'),
               path('profile',views.profile,name='profile')]