from django.urls import path
from accounts import views as Accountview
from . import views


urlpatterns = [
    path('', Accountview.custDashboard, name='custdashboard'),
    path('profile/', views.custProfile, name='custprofile'),
]