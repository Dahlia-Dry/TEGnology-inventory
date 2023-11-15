from django.db import models
from django.contrib.auth.models import User
import datetime
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

STATUS_CHOICES = (('pending','PENDING'),
                  ('delivered','DELIVERED'))

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notify_entry = models.BooleanField(name='Notify by email when new entry added?',default=False)
    notify_order= models.BooleanField(name='Notify by email when new order added?',default=False)
class Product(models.Model):
    name= models.CharField(max_length=200,unique=True)
    pipedrive_id=models.IntegerField(blank=True)
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
        self.address= self.address.replace(',','<br/>')
        self.shipping_address= self.shipping_address.replace(',','<br/>')
        super(Order, self).save(*args, **kwargs)
class Order(models.Model):
    name = models.CharField(max_length=200,unique=True) 
    pipedrive_id = models.IntegerField(primary_key=True)
    last_updated = models.DateField()
    close_date = models.DateField(blank=True,null=True)
    pipedrive_meta = models.JSONField()
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True)
    total = models.FloatField()
    currency = models.CharField(max_length=3,blank=True,null=True)
    order_number=models.CharField(max_length=20,blank=True,null=True)
    def get_edit_url(self):
        return f'https://tegnology2.pipedrive.com/deal/{self.pipedrive_id}'
    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)


class Purchase(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    purchase_number=models.CharField(max_length=20,null=True)
    status=models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    quantity=models.IntegerField()
    unit_price=models.FloatField()
    currency = models.CharField(max_length=3)
    order_date = models.DateField()
    delivery_date = models.DateField(blank=True,null=True)
    def get_edit_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    def save(self, *args, **kwargs):
        self.currency = self.order.currency
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
    order=models.OneToOneField(Order,on_delete=models.CASCADE)
    invoice_number= models.CharField(max_length=20,null=True)
    created_date=models.DateField(blank=True,null=True)
    due_date=models.DateField(blank=True,null=True)
    contact_person=models.CharField(max_length=100,blank=True,null=True)
    contact_email=models.CharField(max_length=100,blank=True,null=True)
    vat = models.FloatField(default=0,verbose_name="VAT (%)")
    #vat2 = models.FloatField(default=0,name="VAT")
    total_vat = models.CharField(max_length=50,blank=True,null=True)
    invoice_file = models.FilePathField(blank=True,null=True)

    def save(self, *args, **kwargs):
        if self.vat is None:
            self.vat=0
        self.total_vat = self.order.currency+f' {(self.order.total*(1+self.vat/100)):.2f}'
        super(Invoice, self).save(*args, **kwargs)