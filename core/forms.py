from django import forms
from .models import *

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields ='__all__'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields ='__all__'
        exclude=['user']