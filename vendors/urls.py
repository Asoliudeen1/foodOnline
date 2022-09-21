from django.urls import path
from .import views
from accounts import views as accountviews

urlpatterns = [
path('', accountviews.vendorDashboard, name='vendordashboard'),
path('registerVendor/', views.registerRestaurant, name='registervendor'),
path('profile/', views.VendorProfile, name='vendor-profile')
]