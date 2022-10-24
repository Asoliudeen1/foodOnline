from django.urls import path
from accounts import views as Accountview
from . import views


urlpatterns = [
    path('', Accountview.custDashboard, name='custdashboard'),
    path('profile/', views.custProfile, name='custprofile'),
    path('my_orders/', views.MyOrders, name='my_orders'),
    path('order_details/<int:order_number>/', views.OrderDetails, name='order_details'),
]