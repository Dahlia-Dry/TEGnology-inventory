from django import forms
from .models import *
class DateInput(forms.DateInput):
    input_type = 'date'

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields ='__all__'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields ='__all__'
        exclude=['user']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields ='__all__'

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields ='__all__'
        exclude=['filepath','line_items','total','total_vat','currency','sent_date']
        widgets = {
            'created_date': DateInput(),
            'due_date': DateInput(),
        }

class InvoiceDateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sent_date'].required = True
    class Meta:
        model = Invoice
        fields =['sent_date']
        widgets = {
            'sent_date': DateInput(),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields =['name','order_number','contact_person','contact_email','notes']

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields=['status','status_date']
        widgets = {
            'status_date': DateInput(),
        }
