from dataclasses import fields
from distutils.command.clean import clean
from pyexpat import model
from django import forms
from .models import User


class UserForm (forms.ModelForm):
    
    # We created pass and confirm pass cos we customize our User Model
    password= forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    # this method confirm if password and confirm_password Match  (non field error)
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get ('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match"
            )