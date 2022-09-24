from multiprocessing import context
from unicodedata import category
from django. contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from accounts.forms import UserForm, UserProfileForm
from accounts.models import User, UserProfile
from menu.models import Category
from vendors.forms import vendorForm
from accounts.utils import  send_verification_email
from .utils import get_vendor
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from vendors.models import Vendor
from menu.forms import CategoryForm
from django.template.defaultfilters import slugify




@login_required(login_url='login')
@user_passes_test(check_role_vendor)
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


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def VendorProfile(request):
    # Note: im using different methods to put my skills into practice

        # first method to get current vendor and profile or current user
    # vendor = request.user.user
    # profile = vendor.user_profile
    
    profile = UserProfile.objects.get(user=request.user)
    vendor = Vendor.objects.get(user=request.user)
    

    #profile = get_object_or_404 (UserProfile, user=request.user)
    #vendor = get_object_or_404 (Vendor, user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = vendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Restaurant updated')
            return redirect('vendor-profile')
        else:
            messages.success(request, 'An Error occurred during registration!')
    
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = vendorForm(instance=vendor)

    context ={
        'profile_form': profile_form, 'vendor_form': vendor_form, 'profile':profile, 'vendor': vendor,
    }
    return render(request, 'vendor/vendor_profile.html', context)


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

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def MenuBuilder(request):
    vendor = get_vendor(request)
    categories = vendor.category_set.all().order_by('created_at')
     # categories = Category.objects.filter(vendor=vendor)
    context = {'categories': categories}
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk):
    
    vendor = get_vendor(request)
    category = vendor.category_set.get(id=pk)
    fooditems = category.fooditem_set.all()
    
    # vendor = Vendor.objects.get(user=request.user)
    # category = get_object_or_404 (Category, id=pk)
    # fooditems = FoodItem.objects.filter(Vendor=vendor, category=category)
    
    context = {
        'fooditems': fooditems,
        'category': category,
    }

    return render (request, 'vendor/fooditems_by_category.html', context)


def AddCategory(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_name = category_form.cleaned_data['category_name']
            category = category_form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category_form.save()
            messages.success(request, 'Category added successfully')
            return redirect('menu-builder')
        else: 
            messages.error(request, 'Data already exist')
    else:
        category_form = CategoryForm()

    context = {
        'category_form': category_form,
    }
    return render(request, 'vendor/add-category.html', context)


def EditCategory(request, pk):
    category = Category.objects.get(id=pk)
    if request.method == 'POST':
        category_form = CategoryForm(request.POST, instance=category)
        if category_form.is_valid():
            category_name = category_form.cleaned_data['category_name']
            category = category_form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category_form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('menu-builder')
        else: 
            messages.error(request, 'Data already exist')
    else:
        category_form = CategoryForm(instance=category)

    context = {
        'category_form': category_form,
        'category': category,
    }
    return render (request, 'vendor/edit-category.html', context)


def DeleteCategory(request, pk):
    category = Category.objects.get(id=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully')
    return redirect('menu-builder')