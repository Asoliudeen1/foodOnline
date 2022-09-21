from multiprocessing import context
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect

from vendors.models import Vendor
from .utils import detectUser, send_verification_email
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


            mail_subject = 'Please Activate your Account'   
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)  #send_verification_email is function created in utils.py
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
    #vendor = Vendor.objects.get(user=request.user)
    # context= {
    #     'vendor': vendor,
    # }
    return render (request, 'vendor/vendordashboard.html')



#Activate the User by setting the is_active status to True
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation!, Your Account is Activated")
        return redirect('myaccount')
    else:
        messages.error(request, 'Invalid Activation link')
    return



def ForgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        # Check if the Email is Exist in the databse
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Send reset Password Email
            mail_subject = 'Reset Your Password'   
            email_template = 'accounts/emails/reset-passord-email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            redirect('login')
        else:
            messages.error(request, 'Email does not exist')
            redirect('forgot-password')
    return render(request, 'accounts/forgot-password.html')


# Reset Password Validation function
def ResetPasswordValidate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid   #store uid in the Session so as to use it on reset Password Page
        return redirect('reset-password')
    else:
        messages.error(request, 'The link has expired!')
        return render('myAccount')
    

def ResetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')  # get the UID (current user id) stored in the session when User click Validate Link
            user = User.objects.get(pk=pk)
            user.set_password(password)   # the set_password function will convert Password to base64
            user.is_active = True
            user.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('login')
        else:
            messages.error(request, "Password and Confirm Password does not match")
            return redirect('reset-password')
    return render(request, 'accounts/reset-password.html')