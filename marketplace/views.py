
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from accounts.models import UserProfile
from marketplace.context_processors import get_cart_counter, get_cat_amount
from menu.models import Category, FoodItem
from orders.forms import OrderForm
from vendors.models import Vendor, OpeningHour
from django.db.models import Prefetch
from datetime import date, datetime

from .models import Cart
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance



def MarketPlace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()

    context= {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/marketplace.html', context)


def VendorDetail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories= Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    
    # opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    opening_hours = vendor.openinghour_set.all().order_by('day', '-from_hour')
    
    # CHECK CURRENT DAY's OPENING HOURS
    today_date = date.today()
    today = today_date.isoweekday() # It will return (1 TO 7)

    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
    
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")

    # # CHECK CURRENT OPENING Time
    # is_open = None
    # for i in current_opening_hours:
    #     start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
    #     end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
    #     if current_time > start and current_time < end:
    #         is_open = True
    #         break
    #     else:
    #         is_open = False

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
    }
    return render(request, 'marketplace/vendor_detail.html', context)


#INCREASE CART
@login_required(login_url ='login')
def AddToCart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #check if the fooditem Exist
            try:
                fooditem = FoodItem.objects.get(id=food_id)

                # Check if the user has already added that food to the Cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the Cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cat_amount(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the food to the Cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cat_amount(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


# DECREASE CART
@login_required(login_url ='login')
def DecreaseCart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #check if the fooditem Exist
            try:
                fooditem = FoodItem.objects.get(id=food_id)

                # Check if the user has already added the food to the Cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    
                    # Decrease the Cart quantity
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0

                    return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cat_amount(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your Cart'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})



def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


@login_required(login_url ='login')
def DeleteCart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Check if the Cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart item Deleted', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cat_amount(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})


def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET.get('address')
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET.get('keyword')

        # GET VENDOR IDS THAT HAS the food item the user is looking for 
        fetch_vendor_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('Vendor', flat=True)
        
        # NORMAL SEARCH 
        #vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        
        # LOCATION BASED SEARCH 
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))

            vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems) | Q(
            vendor_name__icontains=keyword, is_approved=True, user__is_active=True), 
            user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for v in vendors:
                v.kms = round(v.distance.km, 1)


    vendor_count = vendors.count()
    context ={
        'vendors': vendors,
        'vendor_count': vendor_count,
        'source_location': address,
    }
    
    return render(request, 'marketplace/marketplace.html', context)


@login_required(login_url ='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('marketplace')


    user_profile = UserProfile.objects.get(user=request.user)
    deafult_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }

    form = OrderForm(initial=deafult_values)
    context = {
        'form': form,
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)


