from django. contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse 
from accounts.forms import UserForm, UserProfileForm
from accounts.models import User, UserProfile
from menu.models import Category, FoodItem
from orders.models import Order, OrderedFood
from vendors.forms import vendorForm, OpeningHourForm
from accounts.utils import  send_verification_email
from .utils import get_vendor
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from vendors.models import OpeningHour, Vendor
from menu.forms import CategoryForm, FooditemForm
from django.template.defaultfilters import slugify





def registerRestaurant(request):
     # this restrict user from going to Vendor Registration Page after Logged in 
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('vendordashboard')


    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = vendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            vendor_name = v_form.cleaned_data['vendor_name']
            user = form.save(commit=False)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor.vendor_slug = slugify(vendor_name) + '' + str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
           
            mail_subject = 'Please Activate your Account'   
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)   #send_verification_email is function created in utils.py
            messages.success(request, "Your Account has been Registered Successfully, Please Wait for Approval")
            return redirect('registervendor') 
        else:
            messages.error(request, 'An Error occurred during registration!')
    
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
    
    profile = get_object_or_404 (UserProfile, user=request.user)
    vendor = get_object_or_404 (Vendor, user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = vendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Restaurant updated')
            return redirect('vendor-profile')
        else:
            messages.error(request, 'An Error occurred during registration!')
    
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
    #categories = vendor.category_set.all().order_by('created_at')
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {'categories': categories}
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk):
    vendor = get_vendor(request)
    category = get_object_or_404 (Category, id=pk)
    fooditems = FoodItem.objects.filter(Vendor=vendor, category=category)
    
    context = {
        'fooditems': fooditems,
        'category': category,
    }

    return render (request, 'vendor/fooditems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def AddCategory(request):
    venddor = get_vendor(request)
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        #if Category.objects.filter(category_name__iexact=category_name).exists():
        if category_form.is_valid():
            category_name = category_form.cleaned_data['category_name']
            category = category_form.save(commit=False)
            category.vendor = get_vendor(request)
            category.save()
            category.slug = slugify(category_name)+'-'+str(category.id)
            category.save()
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


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def EditCategory(request, pk):
    category = Category.objects.get(id=pk)
    if request.method == 'POST':
        category_form = CategoryForm(request.POST, instance=category)
        if category_form.is_valid():
            category_name = category_form.cleaned_data['category_name']
            category = category_form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category.save()
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


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def DeleteCategory(request, pk):
    category = Category.objects.get(id=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully')
    return redirect('menu-builder')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def Addfooditem(request):
    if request.method == 'POST':
        form = FooditemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            fooditem = form.save(commit=False)
            fooditem.Vendor = get_vendor(request)
            fooditem.slug = slugify(food_title)
            fooditem.save()
            messages.success(request, 'Food added successfully')
            return redirect('fooditems_by_category', fooditem.category.id)
        else:
            messages.error(request, 'Data already exist')
    else:
        form = FooditemForm()

        # modify form so as to select Category of current User
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context ={'form': form,}
    return render(request, 'vendor/add-fooditem.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def Editfooditem(request, pk):
    #fooditem = FoodItem.objects.get(id=pk)
    fooditem = get_object_or_404(FoodItem, id=pk)
   
 
    if request.method == 'POST':
        form = FooditemForm (request.POST, request.FILES, instance=fooditem)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            fooditem = form.save(commit=False)
            fooditem.vendor = get_vendor(request)
            fooditem.slug = slugify(food_title)
            fooditem.save()
            messages.success(request, 'Category updated successfully')
            return redirect('fooditems_by_category', fooditem.category.id)
        else:
            messages.error(request, 'An Error occurred during registration!')
    else:
         form = FooditemForm(instance=fooditem)

        # modify form so as to select Category of current User
         form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form' : form,
        'fooditem': fooditem,
    }
    return render(request, 'vendor/edit-fooditem.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def Deletefooditem(request, pk):
    food = FoodItem.objects.get(id=pk)
    food.delete()
    messages.success(request, 'Food has been deleted successfully')
    return redirect('fooditems_by_category', food.category.id)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def openingHours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm

    context = {
        'form': form,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendor/opening_hour.html', context)


def openingHoursAdd(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            
            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day':day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day':day.get_day_display(), 'from_hour': from_hour, 'to_hour': to_hour}
                return JsonResponse(response)

            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour+'-'+to_hour+' already exists for this day!'}
                return JsonResponse(response)

        else:
            HttpResponse('Invalid request')
    return HttpResponse('add opening hour')


def openingHoursEdit(request, pk):
    pass


def removeopeningHours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})

def OrderDetail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__Vendor=get_vendor(request))
        context ={
            'order': order,
            'ordered_food':ordered_food,
            'subtotal': order.get_total_by_vendor()['subtotal'],
            'tax_data': order.get_total_by_vendor()['tax_dict'],
            'grand_total': order.get_total_by_vendor()['grand_total'],
        }
        return render(request, 'vendor/order_detail.html', context)
    except:
        return redirect('vendordashboard')
    

def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    context= {
        'orders': orders,
    }
    return render(request, 'vendor/my_orders.html', context)