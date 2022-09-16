from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django. contrib import messages


def registerUser(request):
    if request.method == 'POST':
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