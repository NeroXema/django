from django.shortcuts import render,redirect
from .models import Category, Product, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.db.models import Q
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress

# Create your views here.

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product':product})

def category(request, foo):
    foo = foo.replace('-', ' ')  #replace hyphens with space
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category})
    except:
        messages.success(request, ('That Category does not exist!!'))
        return redirect('home')
    
def category_summery(request):
    categories = Category.objects.all()
    return render(request, 'category_summery.html', {"categories":categories})

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products':products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            current_user = Profile.objects.get(user__id=request.user.id)    # Do some shopping cart
            saved_cart = current_user.old_cart   # Get their saved cart from database
            if saved_cart:    # Convert database string to python dictionary
                converted_cart = json.loads(saved_cart)     # Convert to dictionary using JSON
                cart = Cart(request)    # Get the cart / Add the loaded cart dictionary to our session 
                for key,value in converted_cart.items():   # loop thru the cart and add the items from the database
                    cart.db_add(product=key, quantity=value)
            messages.success(request, ('Login successful'))
            return redirect('home')
        else:
            messages.success(request, ('There was an error try again'))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ('Logout successful'))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #login user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ('Username created. Please fill out your info below...'))
            return redirect('update_info')
        else:
            messages.success(request, ('Your Password are not strong enough. please follow by rules!!!'))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})
    
def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, 'User has been Updated.')
            return redirect('home')
        return render(request, 'update_user.html', {"user_form":user_form})
    else:
        messages.error(request, 'You Must Be Login First')
        return redirect('home')
    
def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, ('Your Password Have Been Update.'))
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form':form})
    else:
        messages.error(request, ('You Must Be login to view page'))
        return redirect('home')
    
def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)    # Get current user
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)  # Get current user's shipping info
        form = UserInfoForm(request.POST or None, instance=current_user)    # Get original user form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)     # Get user's shipping form
        if form.is_valid() or shipping_form.is_valid():
            form.save()    #save original form
            shipping_form.save()    #save shipping form
            messages.success(request, 'Your Info has been Updated.')
            return redirect('home')
        return render(request, 'update_info.html', {"form":form, 'shipping_form':shipping_form})
    else:
        messages.error(request, 'You Must Be Login First')
        return redirect('home')
    
def search(request):
   if request.method == 'POST':
        searched = request.POST['searched']
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        if not searched:
            messages.error(request, 'The product you search is not exist!!')
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched':searched})
   else:
        return render(request, 'search.html', {})