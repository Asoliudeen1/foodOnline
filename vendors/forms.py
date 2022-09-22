from dataclasses import fields
from pyexpat import model
from .models import Vendor
from django import forms
from accounts.validators import allow_only_images

class vendorForm(forms.ModelForm):

    vendor_lincense = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images])
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_lincense']