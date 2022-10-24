import simplejson as json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from orders.models import Order, OrderedFood
from .forms import UserProfileForm, UserInfoForm
from accounts.models import User, UserProfile
from django.contrib import messages


@login_required(login_url='login')
def custProfile(request):
    user = request.user
    profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        user_form = UserInfoForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully !')
            return redirect('custprofile')   
        else:
            pass

    else:
        user_form = UserInfoForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    context={
        'user_form': user_form,
        'profile_form':profile_form,
        'profile': profile,
    }
    return render(request, 'customers/customer_profile.html', context)


def MyOrders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'customers/my-orders.html', context)

def OrderDetails(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'tax_data': tax_data,
            'subtotal': subtotal
            }
        return render(request, 'customers/order_details.html', context) 
    except:
        return redirect('custdashboard')

    
    