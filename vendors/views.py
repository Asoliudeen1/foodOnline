from django. contrib import messages
from django.shortcuts import render, redirect
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from vendors.forms import vendorForm
from accounts.utils import  send_verification_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

def registerRestaurant(request):
    # this restrict user from going to Vendor Registration Page after Logged in 
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('dashboard')

    elif request.method == 'POST':
        form = UserForm(request.POST)
        v_form = vendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            password = form.cleaned_data['password'] # clean_data will return 'dict value'
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
           
            mail_subject = 'Please Activate your Account'   
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)   #send_verification_email is function created in utils.py
            messages.success(request, "Your Account has been Registered Successfully, Please Wait for Approval")
            return redirect('registervendor') 
    
    else:
        form = UserForm()
        v_form = vendorForm()
    context = {
        'form': form,
        'v_form': v_form,
    }
    return render(request, 'vendor/registervendor.html', context)


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