from django.urls import path
from .import views


urlpatterns = [
    path('registerUser/', views.registerUser, name='registeruser'),

    path('login/', views.Login, name='login'),
    path('logout/', views.LogOut, name='logout'),
    path('myaccount/', views.myAccount, name='myaccount'),
    path('custdashboard/', views.custDashboard, name='custdashboard'),
    path('vendordashboard/', views.vendorDashboard, name='vendordashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Forgot and Reset Password Path
    path('forgot_password/', views.ForgotPassword, name='forgot-password'),
    path('reset_password_validate/<uidb64>/<token>/', views.ResetPasswordValidate, name='reset-passord-validate'),
    path('reset_password/', views.ResetPassword, name='reset-password'),
]