from django.contrib import admin
from django.urls import path, include
from .import views


urlpatterns = [
    path('place-order/', views.PlaceOrder, name='place-order'),
    path('payments/', views.Payments, name='payments'),
    path('order_complete/', views.OrderComplete, name='order-complete'),
]