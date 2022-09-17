from django.shortcuts import render, redirect

from .utils import detectUser
from .forms import UserForm
from .models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied



# Restrict Vendor from Accessing Customer Page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied



# Restrict Vendor from Accessing Customer Page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied



def registerUser(request):
     # this code restrict user from going to Customer Registration Page after Logged in
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('myaccount')

    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # One of Methods to Handling User Data or Form Data (Creation of user Using Form)
            password = form.cleaned_data['password'] # clean_data will return 'dict value'
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, "Your Account has been Registered Successfully")

            # Second Method to Handling User Data or Form Data (Creation of user Using Create_User Method)
            #first_name = form.cleaned_data['first_name']
            #last_name = form.cleaned_data['last_name']
            #username = form.cleaned_data['username']
            #email = form.cleaned_data['email']
            #password = form.cleaned_data['password']
            #user = User.objects.create_user(first_name = first_name, last_name = last_name, username = username, email = email, password = password)
            #user.role = User.CUSTOMER
            #user.save()

            return redirect ('registeruser')
        else:
            print('Invalid Form')
            print (form.errors)
            
    else:
        form = UserForm()
    context = {'form':form}
    return render (request, 'accounts/registeruser.html', context)

def Login(request):
    
    # # this code restrict user from going to login Page after Logged in 
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('myaccount')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "Email does not exist")
        
        # check if email and Pass is existing in the User Table
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('myaccount')
        else:
            messages.error(request, "Username or Password does not Exist")
            return redirect('login')
    return render (request, 'accounts/login.html')

def LogOut(request):
    logout(request)
    messages.info(request, 'You are Successfully Logout')
    return redirect('login')


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)  #detectUser is function created in utis.py
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render (request, 'accounts/custdashboard.html')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render (request, 'vendor/vendordashboard.html')