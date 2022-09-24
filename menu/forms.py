from dataclasses import fields
from xml.parsers.expat import model
from django.forms import ModelForm
from .models import Category

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']
        