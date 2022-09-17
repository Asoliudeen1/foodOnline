from dataclasses import fields
from pyexpat import model
from .models import Vendor
from django import forms

class vendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_lincense']