from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages
from django.contrib.auth.models import User
from store.models import Product, Profile
import datetime

# Create your views here.

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # get the order
        order = Order.objects.get(id=pk)
        # get the order item
        items = OrderItem.objects.filter(order=pk)
        if request.POST:
            status = request.POST['shipping_status']
            #check if true or false
            if status == 'true':
                order = Order.objects.filter(id=pk)
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                order = Order.objects.filter(id=pk)
                order.update(shipped=False)
            messages.success(request, 'Shipping status Updated')
            return redirect('home')
        return render(request, 'payment/orders.html', {'order':order, 'items':items})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now() #grab date and time
            order.update(shipped=True, date_shipped=now) #update order
            messages.success(request, 'Shipping status Updated')
            return redirect('home')
        return render(request, "payment/not_shipped_dash.html", {'orders':orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now() #grab date and time
            order.update(shipped=False) #update order
            messages.success(request, 'Shipping status Updated')
            return redirect('home')
        return render(request, "payment/shipped_dash.html", {'orders':orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        payment_form = PaymentForm(request.POST or None)    # Get billing info from the last page
        my_shipping = request.session.get('my_shipping')    # Get shipping session data
        # gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        if request.user.is_authenticated:   # logged in
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            # Add order items
            # Get the order id
            order_id = create_order.pk
            # Get product info
            for product in cart_products():
                product_id = product.id     # Get product ID
                if product.is_sale:    # Get product price
                    price = product.sale_price
                else:
                    price = product.price
                # Get quantity
                for key,value in quantities().items():
                    if int(key) == product.id:
                        # create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()
            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.session[key]
            #delete cart from database(old_cart field)
            current_user = Profile.objects.filter(user__id = request.user.id)
            #delete shoppig cart in database(old_cart field)
            current_user.update(old_cart="")
            messages.success(request, "Order Placed")
            return redirect('home')
        else:   # not logged in
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            # Add order items
            # Get the order id
            order_id = create_order.pk
            # Get product info
            for product in cart_products():
                product_id = product.id     # Get product ID
                if product.is_sale:    # Get product price
                    price = product.sale_price
                else:
                    price = product.price
                # Get quantity
                for key,value in quantities().items():
                    if int(key) == product.id:
                        # create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
            #delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    #delete the key
                    del request.session[key]
            messages.success(request, "Order Placed")
            return redirect('home')
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        my_shipping = request.POST  # create a session with shipping info
        request.session['my_shipping'] = my_shipping
        if request.user.is_authenticated:   # check to see if user is logged in
            billing_form = PaymentForm()    # get the billing form
            return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities": quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})
        else:   # not logged in
            billing_form = PaymentForm()    # get the billing form
            return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities": quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})
        shipping_form = request.POST
        return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities": quantities, "totals":totals, "shipping_form":shipping_form})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def payment_success(request):
    return render(request, "payment/payment_success.html", {})


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        # checkout as logged in use
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)   # shipping user
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)  # shipping form
        return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities": quantities, "totals":totals, "shipping_form":shipping_form})
    else:
        # checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities": quantities, "totals":totals, "shipping_form":shipping_form})