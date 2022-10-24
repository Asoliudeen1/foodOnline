import simplejson as json
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from marketplace.models import Cart
from marketplace.context_processors import get_cat_amount
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
from .utils import generate_order_number
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def PlaceOrder(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    subtotal = get_cat_amount(request)['subtotal']
    total_tax = get_cat_amount(request)['tax']
    grand_total = get_cat_amount(request)['grand_total']
    tax_data = get_cat_amount(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save() # Order id/pk generated
            order.order_number = generate_order_number(order.id)
            order.save()
            context ={
                'order':order,
                'cart_items':cart_items,
            }
            return render(request, 'orders/place-order.html', context)
        else:
            print(form.errors)

    return render(request, 'orders/place-order.html')


@login_required(login_url='login')
def Payments(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user, 
            transaction_id=transaction_id, 
            payment_method=payment_method,
            amount = order.total,
            status = status
        )
        payment.save()


        #UPDATE THE ORDER MODEL
        order.payment = payment
        order.is_ordered = True
        order.save()

        # MOVE THE CART ITEMS TO ORDERED FOOD MODEL
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity #total amount
            ordered_food.save()
        

        # SEND ORDER CONFIRMATION TO THE CUSTOMER
        mail_subject = 'Thank you for ordering with us'
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }
        send_notification(mail_subject, mail_template, context)

        # SEND ORDER RECIEVED EMAIL TO VENDOR
        mail_subject = 'You have a new Order'
        mail_template = 'orders/new_order.html'
        to_emails = []
        for i in cart_items:
            if i.fooditem.Vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.Vendor.user.email)
        context = {
            'order': order,
            'to_email': to_emails,
        }
        send_notification(mail_subject, mail_template, context)


        # CLEAR THE CART ONCE PAYMENT IS SUCCESSFUL
        #cart_items.delete()

        response = {
            'order_number': order_number,
            'transaction_id': transaction_id
        }
        return JsonResponse(response)
    return HttpResponse('payments view')



def OrderComplete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    print(transaction_id)
    print(order_number)

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        
        print(order)
        print(ordered_food)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data':tax_data
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')