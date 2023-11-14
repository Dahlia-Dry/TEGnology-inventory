import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')
django.setup()

import pdfkit
from django.template.loader import render_to_string

