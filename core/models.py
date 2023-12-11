from django.db import models
from django.contrib.auth.models import User
import datetime
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notify_new_entry = models.BooleanField(name='Notify by email when new entry added?',default=False)
    notify_new_order= models.BooleanField(name='Notify by email when new order added?',default=False)
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
        DEAL_PENDING=0
        QUOTATION_SENT=1
        PURCHASE_ORDER_RECEIVED=2
        ORDER_CONFIRMATION_SENT=3
        INVOICE_SENT=4
        DELIVERY_SCHEDULED=5
        DELIVERY_CONFIRMED=6

    def get_status(self):
        return self.Status(self.status).label
    name = models.CharField(max_length=200,unique=True) 
    pipedrive_id = models.IntegerField(primary_key=True)

    status = models.IntegerField(choices=Status.choices, default=Status.QUOTATION_SENT)
    prev_status= models.IntegerField(choices=Status.choices, default=Status.QUOTATION_SENT)
    status_date=models.DateField(blank=True,null=True)
    prev_status_date= models.DateField(blank=True,null=True)

    close_date = models.DateField(blank=True,null=True)
    pipedrive_meta = models.JSONField()

    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True)
    contact_person=models.CharField(max_length=100,blank=True,null=True)
    contact_email=models.CharField(max_length=100,blank=True,null=True)
    
    total = models.FloatField(blank=True,null=True)
    vat = models.FloatField(default=25,verbose_name="VAT (%)",blank=True,null=True)
    currency = models.CharField(max_length=3,blank=True,null=True)
    order_number=models.CharField(max_length=20,blank=True,null=True)

    quotation=models.ForeignKey("Quotation",blank=True,null=True,on_delete=models.SET_NULL)
    purchase_order=models.ForeignKey("PurchaseOrder",blank=True,null=True,on_delete=models.SET_NULL)
    order_confirmation=models.ForeignKey("OrderConfirmation",blank=True,null=True,on_delete=models.SET_NULL)
    invoice=models.ForeignKey("Invoice",blank=True,null=True,on_delete=models.SET_NULL)
    delivery_notice=models.ForeignKey("DeliveryNotice",blank=True,null=True,on_delete=models.SET_NULL)

    notes = models.TextField(blank=True,null=True)
    
    def __str__(self):
        return self.name
    def get_edit_url(self):
        return f'https://tegnology2.pipedrive.com/deal/{self.pipedrive_id}'
    def save(self, *args, **kwargs):
        try:
            t = float(self.total)
            self.total = f"{t:.2f}"
            self.total_vat = self.currency+f' {t*(1+self.vat/100):.2f}'
            self.vat_amt = self.currency+f' {t*(self.vat/100):.2f}'
        except Exception as e:
            print(e)
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
    def __str__(self):
        return f"{self.quantity}x{self.product} - arrival date {self.date}\n {self.notes}"
    def get_edit_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
class Invoice(models.Model):
    #base fields
    filepath = models.FilePathField() #can be generated or user upload
    sent_date= models.DateField(verbose_name='sent date',blank=True,null=True)

    #used for generating file from template
    invoice_number= models.CharField(max_length=20,null=True)
    created_date=models.DateField(blank=True,null=True)
    due_date=models.DateField(blank=True,null=True)
    contact_person=models.CharField(max_length=100,blank=True,null=True)
    contact_email=models.CharField(max_length=100,blank=True,null=True)
    sender_email=models.CharField(max_length=50,blank=True,null=True)

class PurchaseOrder(models.Model):
    po_number= models.CharField(max_length=20,null=True)
    filepath = models.FilePathField()
    received_date=models.DateField(null=True)
class OrderConfirmation(models.Model):
    #base fields
    filepath = models.FilePathField() #can be generated or user upload
    sent_date= models.DateField(verbose_name='sent date',blank=True,null=True)

    #used for generating file from template
    created_date=models.DateField(blank=True,null=True)
    contact_person=models.CharField(max_length=100,blank=True,null=True)
    contact_email=models.CharField(max_length=100,blank=True,null=True)
    sender_email=models.CharField(max_length=50,blank=True,null=True)
    message = models.TextField(blank=True,null=True)

class DeliveryNotice(models.Model):
    #base fields
    filepath = models.FilePathField() #can be generated or user upload
    sent_date= models.DateField(verbose_name='sent date',blank=True,null=True)

    #used for generating file from template
    order_number= models.CharField(max_length=20,null=True)
    created_date=models.DateField(blank=True,null=True)
    delivery_date=models.DateField(blank=True,null=True)
    contact_person=models.CharField(max_length=100,blank=True,null=True)
    contact_email=models.CharField(max_length=100,blank=True,null=True)
    message = models.TextField(blank=True,null=True)
    sender_email=models.CharField(max_length=50,blank=True,null=True)


class Quotation(models.Model):
    #base fields
    filepath = models.FilePathField() #can be generated or user upload
    sent_date= models.DateField(verbose_name='sent date',blank=True,null=True)
    
    #used for generating file from template
    quotation_number= models.CharField(max_length=20,null=True)
    created_date=models.DateField(blank=True,null=True)
    due_date=models.DateField(blank=True,null=True)
    contact_person=models.CharField(max_length=100,blank=True,null=True)
    contact_email=models.CharField(max_length=100,blank=True,null=True)
    message = models.TextField(blank=True,null=True)
    sender_email=models.CharField(max_length=50,blank=True,null=True)

class Timestamp(models.Model):
    label = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now= True)