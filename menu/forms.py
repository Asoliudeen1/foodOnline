

from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from accounts.validators import allow_only_images
from .models import Category, FoodItem

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']


class FooditemForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}), validators=[allow_only_images])
    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'image', 'is_available']

        