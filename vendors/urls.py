from django.urls import path
from .import views


urlpatterns = [
path('registerVendor/', views.registerRestaurant, name='registervendor')
]