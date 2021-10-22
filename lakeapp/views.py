import uuid
import requests
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.forms import PasswordChangeForm  
from django.contrib import messages

from . forms import SignupForm
from . models import Category, Product, Shopcart, Carousel, Payment
# Create your views here.
def index(request):
    featured = Product.objects.filter(featured=True).filter(available=True)
    latest = Product.objects.filter(latest=True)
    available =Product.objects.filter(available=True)
    
    context = {
        'featured':featured,
        'latest':latest,
        'available':available,
    }
    
    return render(request, 'index.html', context)



def categories(request):
    categories = Category.objects.all()

    context = {
        'categories':categories
    }
    return render(request, 'categories.html',context)


def logoutfunc(request): 
    logout(request)
    return redirect('loginform')

def loginform(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user:
            login(request,user)
            messages.success(request, 'now logged in as a user!')
            return redirect('index')
        else:
            messages.info(request, 'Username/password incorrect')
            return redirect('loginform')

    return render(request, 'loginform.html')

def signupform(request):
    reg = SignupForm()
    if request.method == 'POST':
        reg = SignupForm(request.POST)
        if reg.is_valid():
            reg.save() 
            messages.success(request, 'Successfully!')
            return redirect('index')
        else:
            messages.warning(request, reg.errors)
            return redirect('signupform')
            
    context ={
        'reg': reg
    }
    return render(request, 'signup.html', context)

def category(request,id):
    category=Product.objects.filter(category_id=id)

    context={
        'category':category
    }
    return render(request, 'category.html', context)


def products(request):
    product=Product.objects.all().filter(available=True)

    context={
        'product':product
    }
    return render(request, 'products.html', context)


def details(request,id):
    details=Product.objects.get(pk=id)

    context={
        'details':details

    }
    return render(request, 'details.html',context)
    


def password(request):
    update = PasswordChangeForm(request.user)
    if request.method=='POST':
        update=PasswordChangeForm(request.user, request.POST)
        if update.is_valid():
            user=update.save()
            update_session_auth_hash(request,user)
            messages.success(request, 'Password Update Successful')
            return redirect('index')
        else:
            messages.error(request, update.errors)
            return redirect('password')

    context={
        'update':update
    }
    return render(request, 'password.html', context)


def addtocart(request):
    if request.method == 'POST':
        basket_num = str(uuid.uuid4())
        vol = int(request.POST['quantity'])
        pid = request.POST['itemid']
        item = Product.objects.get(pk=pid)
        cart = Shopcart.objects.filter(user__username= request.user.username, paid_order=False)
        if cart:
            basket = Shopcart.objects.filter(user__username=request.user.username, product_id=item.id).first()
            if basket:
                basket.quantity += vol
                basket.save()
                messages.success(request, 'Product added!')
                return redirect('products')
            else:
                newitem = Shopcart()
                newitem.user=request.user
                newitem.product=item
                newitem.basket_no=cart[0].basket_no
                newitem.quantity=vol
                newitem.paid_order=False
                newitem.save()
                messages.success(request, 'New Product added to!')
            

        else:
            newbasket = Shopcart()
            newbasket.user=request.user
            newbasket.product=item
            newbasket.basket_no=basket_num
            newbasket.quantity=vol
            newbasket.paid_order=False
            newbasket.save()
            messages.success(request, 'Product added to Basket!')     
    return redirect('products')


def cart(request):
    cart=Shopcart.objects.filter(user__username=request.user.username, paid_order=False)

 
    subtotal=0
    vol=0
    total=0

    for item in cart:
        subtotal+=item.product.price * item.quantity

    vat=0.075 *subtotal

    total=subtotal + vat


    context={
        'cart':cart,
        'subtotal':subtotal,
        'vat':vat,
        'total':total,
    }
    return render(request, 'cart.html', context)


def checkout(request):
    cart=Shopcart.objects.filter(user__username=request.user.username, paid_order=False)

 
    subtotal=0
    vol=0
    total=0

    for item in cart:
        subtotal+=item.product.price * item.quantity

    vat=0.075 *subtotal

    total=subtotal + vat


    context={
        'cart':cart,
        'total':total,
        'cart_code':cart[0].basket_no
    }
    return render(request, 'checkout.html',context)

def placeorder(request):
    if request.method=='POST':
        api_key='sk_test_11483da27a28a2304414f2ca3be5a7c88bd121a7'
        curl= 'https://api.paystack.co/transaction/initialize'
        cburl= 'http://54.176.0.127/completed'
        total= float(request.POST['total']) *100
        cart_code = request.POST['cart_code']
        pay_code= str(uuid.uuid4())
        user= User.objects.get(username=request.user.username)
        first_name= request.POST['first_name']
        last_name= request.POST['last_name']
        phone= request.POST['phone']
        address= request.POST['address']
        city= request.POST['city']
        state= request.POST['state']

       #collect data that you will send to paystack
        headers={'Authorization':f'Bearer {api_key}'}
        data={'reference':pay_code,'email':user.email,'amount':int(total),'callback_url':cburl,'oredr_number':cart_code}

        #make a call to paystack
        try:
            r=requests.post(curl, headers=headers, json=data)
        except Exception:
            messages.error(request, 'Network busy, try again')
        else:
            transback= json.loads(r.text)
            rd_url= transback['data']['authorization_url']

            paid = Payment ()
            paid.user=user 
            paid.amount=total 
            paid.basket_no=cart_code 
            paid.pay_code=pay_code 
            paid.paid_order=True
            paid.first_name=first_name 
            paid.last_name=last_name 
            paid.phone=phone 
            paid.address=address 
            paid.city=city 
            paid.state=state
            paid.save()

            bag = Shopcart.objects.filter(user__username=request.user.username, paid_order=False)
            for item in bag:
                item.paid_order=True
                item.save()

                stock=Product.objects.get(pk=item.product.id)
                stock.max -=item.quantity
                stock.save()

            return redirect(rd_url)
    return redirect('checkout')

def completed(request):
    user=User.objects.get(username=request.user.username)

    context={
        'user':user 
    }
    return render(request, 'completed.html', context)

def deleteitem(request):
    itemid=request.POST['itemid']
    Shopcart.objects.filter(pk=itemid).delete()
    messages.success(request, 'Product deleted')
    return HttpResponse('cart')


def increase(request):
    itemval=request.POST['itemval']
    valid=request.POST['valid']
    update=Shopcart.objects.get(pk=valid)
    update.quantity=itemval
    update.save
    messages.success(request, 'Product quantity update successfully')
    return redirect('cart') 