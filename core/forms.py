from django import forms
from .models import *
class DateInput(forms.DateInput):
    input_type = 'date'

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields ='__all__'

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields ='__all__'
        exclude=['pipedrive_id']

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
        exclude=['filepath','line_items','total','total_vat','vat_amt','currency','sent_date']
        widgets = {
            'created_date': DateInput(),
            'due_date': DateInput(),
        }

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields ='__all__'
        exclude=['filepath','sent_date','line_items','total','currency']
        widgets = {
            'created_date': DateInput(),
        }

class OrderConfirmationForm(forms.ModelForm):
    class Meta:
        model = OrderConfirmation
        fields ='__all__'
        exclude=['filepath','sent_date','line_items','total','vat_amt','total_vat','currency']
        widgets = {
            'created_date': DateInput(),
        }

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields ='__all__'
        exclude=['filepath']
        widgets = {
            'received_date': DateInput(),
        }

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = DeliveryNotice
        fields ='__all__'
        exclude=['filepath','sent_date','line_items','total','currency']
        widgets = {
            'created_date': DateInput(),
        }

def gen_file_dateform(model_name,data=None,instance=None):
    class FileDateForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['sent_date'].required = True
        class Meta:
            model = model_name
            fields =['sent_date']
            widgets = {
                'sent_date': DateInput(),
            }
    form = FileDateForm(data=data, instance=instance)
    return form
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields =['name','order_number','contact_person','contact_email', 'vat','notes']

class OrderStatusForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status_date'].required = True
    class Meta:
        model = Order
        fields=['status','status_date']
        widgets = {
            'status_date': DateInput(),
        }

class OrderCompleteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status_date'].required = True
    class Meta:
        model = Order
        fields=['status_date']
        widgets = {
            'status_date': DateInput(),
        }
