from django.urls import path
from .import views


urlpatterns = [
    path('registerUser/', views.registerUser, name='registeruser'),

    path('login/', views.Login, name='login'),
    path('logout/', views.LogOut, name='logout'),
    path('myaccount/', views.myAccount, name='myaccount'),
    path('custdashboard/', views.custDashboard, name='custdashboard'),
    path('vendordashboard/', views.vendorDashboard, name='vendordashboard'),
]