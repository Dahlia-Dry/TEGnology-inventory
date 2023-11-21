from django.db import models
from django.contrib.auth.models import User
import datetime
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notify_entry = models.BooleanField(name='Notify by email when new entry added?',default=False)
    notify_order= models.BooleanField(name='Notify by email when new order added?',default=False)
class Product(models.Model):
    name= models.CharField(max_length=200,unique=True)
    pipedrive_id=models.IntegerField(blank=True)
    def __str__(self):
        return self.name
class Customer(models.Model):
    name = models.CharField(max_length=200,unique=True)
    address = models.TextField(max_length=500,blank=True,null=True)
    cvr = models.CharField(max_length=20,blank=True,null=True)
    shipping_address = models.TextField(blank=True,null=True)
    po_number=models.CharField(max_length=20,blank=True,null=True)
    bank_account = models.CharField(max_length=20,blank=True,null=True)
    IBAN=models.CharField(max_length=20,blank=True,null=True)
    SWIFT_BIC=models.CharField(max_length=20,blank=True,null=True)
    bank_name=models.CharField(max_length=20,blank=True,null=True)
    phone=models.CharField(max_length=20,blank=True,null=True)
    email=models.CharField(max_length=20,blank=True,null=True)
    def save(self, *args, **kwargs):
        try:
            self.address = self.address.replace('<br/>','\n')
        except:
            pass
        try:
            self.shipping_address = self.shipping_address.replace('<br/>','\n')
        except:
            pass
        super(Customer, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
class Order(models.Model):
    class Status(models.IntegerChoices):
        DEAL_CLOSED=1
        QUOTATION_SENT=2
        ORDER_CONFIRMATION_SENT=3
        INVOICE_SENT=4
        DELIVERY_SCHEDULED=5
        DELIVERY_CONFIRMED=6

    def get_status(self):
        return self.Status(self.status).label
    name = models.CharField(max_length=200,unique=True) 
    pipedrive_id = models.IntegerField(primary_key=True)

    status = models.IntegerField(choices=Status.choices, default=Status.DEAL_CLOSED)
    status_date=models.DateField(blank=True,null=True)
    prev_status_date= models.DateField(blank=True,null=True)

    close_date = models.DateField(blank=True,null=True)
    pipedrive_meta = models.JSONField()

    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True)
    contact_person=models.CharField(max_length=100,blank=True,null=True)
    contact_email=models.CharField(max_length=100,blank=True,null=True)
    
    total = models.FloatField()
    currency = models.CharField(max_length=3,blank=True,null=True)
    order_number=models.CharField(max_length=20,blank=True,null=True)

    invoice=models.ForeignKey("Invoice",blank=True,null=True,on_delete=models.SET_NULL)

    notes = models.TextField(blank=True,null=True)
    
    def __str__(self):
        return self.name
    def get_edit_url(self):
        return f'https://tegnology2.pipedrive.com/deal/{self.pipedrive_id}'
    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
class Purchase(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    status = models.IntegerField()
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    unit_price=models.FloatField()
    total = models.CharField(max_length=50,blank=True,null=True)
    def save(self, *args, **kwargs):
        try:
            self.total=self.order.currency+f' {(self.quantity*self.unit_price):.2f}'
        except:
            pass
        super(Purchase, self).save(*args, **kwargs)
    
class Entry(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    quantity=models.IntegerField()
    notes = models.TextField(blank=True,null=True)
    user=models.ForeignKey(User,related_name='user',on_delete=models.CASCADE)
    def get_edit_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
class Invoice(models.Model):
    #mandatory fields
    filepath = models.FilePathField() #can be generated or user upload

    sent_date= models.DateField(verbose_name='sent date',blank=True,null=True)

    #used for generating file from template
    invoice_number= models.CharField(max_length=20,null=True)
    created_date=models.DateField(blank=True,null=True)
    due_date=models.DateField(blank=True,null=True)
    contact_person=models.CharField(max_length=100,blank=True,null=True)
    contact_email=models.CharField(max_length=100,blank=True,null=True)
    
    #calculated fields
    line_items = models.JSONField(blank=True,null=True)
    currency = models.CharField(max_length=3,blank=True,null=True)
    total = models.CharField(max_length=50,blank=True,null=True)
    vat = models.FloatField(default=0,verbose_name="VAT (%)")
    total_vat = models.CharField(max_length=50,blank=True,null=True)

    def save(self, *args, **kwargs):
        print('saving')
        
        try:
            t = self.total
            self.total = self.currency + f" {t:.2f}"
            self.total_vat = self.currency+f' {t*(1+self.vat/100):.2f}'
        except Exception as e:
            print(e)
        super(Invoice, self).save(*args, **kwargs)

class Timestamp(models.Model):
    label = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now= True)