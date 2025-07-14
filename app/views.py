from django.shortcuts import render
from .models import Product, Cart, Order, Contact, Blog
from django.http import HttpResponse, JsonResponse
from django.views import View
from .forms import CustomerRegistrationForm, UpdateProfileForm, ContactForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.paginator import Paginator
import paypalrestsdk
from django.conf import settings
from django.urls import reverse

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

# Create your views here.
def create_paypal_payment(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total = sum([item.quantity * item.product.price for item in cart_items])

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('paypal_execute')),
            "cancel_url": request.build_absolute_uri(reverse('checkout')),
        },
        "transactions": [{
            "amount": {
                "total": "%.2f" % total,
                "currency": "USD"
            },
            "description": "Furni order payment"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.method == "REDIRECT":
                redirect_url = str(link.href)
                return redirect(redirect_url)
        return render(request, 'app/checkout.html', {'error': 'PayPal link not found.'})
    else:
        return render(request, 'app/checkout.html', {'error': 'Error creating PayPal payment.'})
    

def execute_paypal_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,
                payment_method='paypal',
                quantity=item.quantity,
                total_cost=item.quantity * item.product.price,
                status='paid',
            )
        cart_items.delete()
        return render(request, 'app/thankyou.html')
    else:
        return render(request, 'app/checkout.html', {'error': 'PayPal payment failed.'})

def home(request):
    return render(request, 'app/home.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def customerregistration(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration Successful')
            return redirect('login')
        else:
            messages.error(request, 'Registration Failed')
    else:
        form = CustomerRegistrationForm() 
    return render(request, 'app/customerregistration.html', {'form': form, 'messages': messages})

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Information updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Update failed. Please check the information again.')
    else:
        form = UpdateProfileForm(instance=request.user)
    return render(request, 'app/profile.html', {'form': form})


def add_to_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    product_id = request.GET.get("prod_id")
    quantity = int(request.GET.get("quantity", 1))
    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, "The quantity of products in the cart has been updated!")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Product added to cart successfully!")
    return redirect('detail', id=product_id)

def show_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    cart_items = []
    for p in cart:
        value = p.quantity * p.product.price
        amount += value
        cart_items.append({
            'item': p,
            'total': value
        })
    return render(request, 'app/cart.html',  {'cart': cart_items, 'totalAmount': amount})

   

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    if not cart_items.exists():
        return redirect('cart')
    if request.method == 'POST':
       
        order_type = request.POST.get('order_type')
        # if form.is_valid():
        if order_type == 'paypal':
            return redirect('paypal_create')
        else:
            for item in cart_items:
                Order.objects.create(
                    user=user,
                    product=item.product,
                    payment_method='cod',
                    quantity=item.quantity,
                    total_cost=item.quantity * item.product.price,
                    status='processing',
                )
            cart_items.delete()
        return redirect('thankyou')
    # Tính tổng tiền
    cart = []
    for item in Cart.objects.filter(user=user):
        cart.append({
            'product': item.product,
            'quantity': item.quantity,
            'total': item.quantity * item.product.price
        })
    total = sum([item.quantity * item.product.price for item in cart_items])
    return render(request, 'app/checkout.html', {
        'cart_items': cart,
        'total': total,
    })


def order_history(request):
    if not request.user.is_authenticated:
        return redirect('login')
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'app/order_history.html', {'orders': orders})


def about(request):
    return render(request, 'app/about.html')

def services(request):
    return render(request, 'app/services.html')

def blog(request):
    blog_list = Blog.objects.all()
    paginator = Paginator(blog_list, 6)  # 5 bài viết mỗi trang

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'app/blog.html', {'page_obj': page_obj})

def contact(request):
    from django.contrib import messages
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            # Lưu vào database
            Contact.objects.create(
                firstname=firstname,
                lastname=lastname,
                email=email,
                message=message
            )
            # Nếu muốn gửi email thì giữ lại đoạn này, còn không thì có thể xóa
            # subject = f'Liên hệ từ {firstname} {lastname}'
            # content = f"Tên: {firstname} {lastname}\nEmail: {email}\nNội dung: {message}"
            # try:
            #     send_mail(subject, content, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            #     messages.success(request, 'Gửi liên hệ thành công!')
            # except Exception:
            #     messages.error(request, 'Gửi liên hệ thất bại. Vui lòng thử lại sau.')
            messages.success(request, 'Contact sent successfully!')
            form = ContactForm()  # reset form
        else:
            messages.error(request, 'Please check the information again.')
    else:
        form = ContactForm()
    return render(request, 'app/contact.html', {'form': form})


def category(request, val):

    products = Product.objects.filter(category=val)
    paginator = Paginator(products, 6) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'app/shop.html', {'page_obj': page_obj})

def shop(request):
    products = Product.objects.all()
    paginator = Paginator(products, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'app/shop.html', {'page_obj': page_obj})

def shop_detail(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'app/shop_detail.html', {'product': product})


def thankyou(request):
    return render(request, 'app/thankyou.html')

def subscribe_newsletter(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        if name and email:
            subject = 'Get the latest updates'
            message = f'Dear {name}, \n\nYou have subscribed to our mailing list. \n\nYou will receive the latest updates from us. \n\nThank you for using our service. \n\nRegards, \n\nFurni Team'
            send_mail(subject, message, '"Furni" <hoangdeptraibodoiqua4321@gmail.com>', [email])
    return redirect(request.META.get('HTTP_REFERER', '/'))

@csrf_exempt
def update_cart(request):
    if request.method == "POST" and request.user.is_authenticated:
        import json
        data = json.loads(request.body)
        product_id = data.get("product_id")
        action = data.get("action")
        user = request.user
        try:
            cart_item = Cart.objects.get(user=user, product_id=product_id)
            if action == "increase":
                cart_item.quantity += 1
            elif action == "decrease" and cart_item.quantity > 1:
                cart_item.quantity -= 1
            cart_item.save()
        except Cart.DoesNotExist:
            return JsonResponse({"error": "No products found in cart"}, status=404)

        # Tính lại tổng
        cart = Cart.objects.filter(user=user)
        amount = 0
        cart_items = []
        for p in cart:
            value = p.quantity * p.product.price
            amount += value
            cart_items.append({
                'id': p.product.id,
                'quantity': p.quantity,
                'total': value
            })
        return JsonResponse({
            "cart_items": cart_items,
            "subtotal": amount,
            "total": amount,
            "product_id": product_id,
            "quantity": cart_item.quantity,
            "item_total": cart_item.quantity * cart_item.product.price
        })
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def remove_cart(request):
    if request.method == "POST" and request.user.is_authenticated:
        import json
        data = json.loads(request.body)
        product_id = data.get("product_id")
        user = request.user
        try:
            cart_item = Cart.objects.get(user=user, product_id=product_id)
            cart_item.delete()
        except Cart.DoesNotExist:
            return JsonResponse({"error": "No products found in cart"}, status=404)

        # Tính lại tổng
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            amount += p.quantity * p.product.price
        return JsonResponse({
            "subtotal": amount,
            "total": amount,
            "product_id": product_id
        })
    return JsonResponse({"error": "Invalid request"}, status=400)
