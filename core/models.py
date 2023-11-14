from django.db import models
from django.contrib.auth.models import User
import datetime
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

STATUS_CHOICES = (('pending','PENDING'),
                  ('delivered','DELIVERED'))

class Product(models.Model):
    name= models.CharField(max_length=200,unique=True,primary_key=True)
    pipedrive_id=models.IntegerField(blank=True)

class Order(models.Model):
    name = models.CharField(max_length=200,unique=True) 
    pipedrive_id = models.IntegerField(primary_key=True)
    last_updated = models.DateField()
    close_date = models.DateField(blank=True,null=True)
    pipedrive_meta = models.JSONField()
    order_number=models.CharField(max_length=20)
    def get_edit_url(self):
        return f'https://tegnology2.pipedrive.com/deal/{self.pipedrive_id}'
    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)


class Purchase(models.Model):
    #purchase_number=models.CharField(max_length=20,unique=True,null=True)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    status=models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    quantity=models.IntegerField()
    unit_price=models.FloatField()
    currency=models.CharField(max_length=3)
    order_date = models.DateField()
    delivery_date = models.DateField(blank=True,null=True)
    def get_edit_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    
class Entry(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    quantity=models.IntegerField()
    user=models.ForeignKey(User,related_name='user',on_delete=models.CASCADE)
    def get_edit_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

class Invoice(models.Model):
    invoice_number= models.CharField(max_length=20,unique=True,primary_key=True)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    company =models.CharField(max_length=100,blank=True,null=True)
    invoice_address=models.TextField(blank=True,null=True)
    cvr_number = models.CharField(max_length=20,blank=True,null=True)
    shipping_address = models.TextField(blank=True,null=True)
    invoice_date = models.DateField(default=datetime.date.today,blank=True,null=True)
    po_number=models.CharField(max_length=20,blank=True,null=True)
    contact_person=models.CharField(max_length=100,blank=True,null=True)
    contact_email=models.CharField(max_length=100,blank=True,null=True)
    invoice_file = models.FilePathField(blank=True,null=True)
