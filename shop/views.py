from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
import random
import string
import razorpay

from .models import (
    Category, Product, ProductImage, Cart, CartItem, Coupon,
    Offer, CustomerDiscountLead, Order, OrderItem, ReturnRequest,
    Banner, Wishlist, ProductReview, ReviewImage, StoreSetting
)
from .forms import ProductReviewForm, ReturnRequestForm, LeadForm, CouponApplyForm
from accounts.models import Address
from .invoice_generator import generate_pdf_invoice

def home_view(request):
    """
    Renders the premium home page with sliding banners, section highlights, and Instagram mockup grids.
    """
    banners = Banner.objects.filter(active=True).order_by('order', 'id')
    featured = Product.objects.filter(is_featured=True, stock__gt=0)[:8]
    new_arrivals = Product.objects.filter(is_new_arrival=True, stock__gt=0).order_by('-id')[:8]
    best_sellers = Product.objects.filter(is_best_seller=True, stock__gt=0)[:8]
    trending = Product.objects.filter(is_trending=True, stock__gt=0)[:8]
    
    # Get 3-4 premium reviews
    reviews = ProductReview.objects.select_related('product', 'user').order_by('-created_at')[:4]
    
    # Mock Instagram images (Premium jewelry stock image paths or placeholders)
    instagram_mock = [
        {'image': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=300&q=80', 'link': '#'},
        {'image': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=300&q=80', 'link': '#'},
        {'image': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=300&q=80', 'link': '#'},
        {'image': 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=300&q=80', 'link': '#'},
        {'image': 'https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?auto=format&fit=crop&w=300&q=80', 'link': '#'},
        {'image': 'https://images.unsplash.com/photo-1599643477877-537ef527852f?auto=format&fit=crop&w=300&q=80', 'link': '#'},
    ]
    
    context = {
    'banners': banners,
    'featured': featured,
    'new_arrivals': new_arrivals,
    'best_sellers': best_sellers,
    'trending': trending,
    'reviews': reviews,
    'instagram_gallery': instagram_mock,
    'announcement': StoreSetting.get_settings().announcement_text,

    'women_categories': Category.objects.filter(parent__name__iexact='women', active=True),
    'men_categories': Category.objects.filter(parent__name__iexact='men', active=True),
    'categories': Category.objects.filter(
    active=True,
    image__isnull=False
).exclude(image='')
}
    return render(request, 'shop/home.html', context)

def category_products_view(request, slug=None):
    """
    Renders the catalog of products filtered by category/collection with advanced sorting.
    """
    category = None
    products = Product.objects.all()
    
    # Get all categories for filter sidebar
    all_categories = Category.objects.all()
    
    # Parent filter collection (men or women)
    gender_filter = request.GET.get('collection', None)
    if gender_filter in ['women', 'men']:
        # Fetch categories belonging to Women/Men Collection
        parent_cat = Category.objects.filter(name__icontains=gender_filter).first()
        if parent_cat:
            sub_ids = parent_cat.subcategories.values_list('id', flat=True)
            products = products.filter(Q(category=parent_cat) | Q(category_id__in=sub_ids))
    
    if slug:
        category = get_object_or_404(Category, slug=slug)
        sub_categories = category.subcategories.all()
        if sub_categories.exists():
            products = products.filter(Q(category=category) | Q(category__in=sub_categories))
        else:
            products = products.filter(category=category)
            
    # Filters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
        
    # Search Query
    q = request.GET.get('q')
    if q:
        products = products.filter(
            Q(name__icontains=q) | 
            Q(description__icontains=q) | 
            Q(category__name__icontains=q)
        )
        
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popularity':
        products = products.order_by('-view_count')
    elif sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
        
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'all_categories': all_categories,
        'sort_by': sort_by,
        'q': q,
        'min_price': min_price,
        'max_price': max_price,
        'collection': gender_filter,
    }
    return render(request, 'shop/category_products.html', context)

def product_detail_view(request, slug):
    """
    Renders the details page of a product with zoom and related cross-sells.
    """
    product = get_object_or_404(Product, slug=slug)
    
    # Track view for popularity ranking
    Product.objects.filter(id=product.id).update(view_count=F('view_count') + 1)
    product.refresh_from_db()
    
    # Related products (same category/parent category, excluding current product)
    related = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    if not related.exists() and product.category.parent:
        related = Product.objects.filter(category__parent=product.category.parent).exclude(id=product.id)[:4]
        
    # Frequently bought together (mocked from related or special offers)
    frequently_bought = Product.objects.exclude(id=product.id).order_by('?')[:2]
    
    # Reviews
    reviews = product.reviews.select_related('user').prefetch_related('images').order_by('-created_at')
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews.exists() else 5.0
    
    review_form = ProductReviewForm()
    
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ProductReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
            # Save uploaded image if exists
            review_image = request.FILES.get('review_image')
            if review_image:
                ReviewImage.objects.create(review=review, image=review_image)
                
            messages.success(request, "Thank you for reviewing this product!")
            return redirect('shop:product_detail', slug=product.slug)
            
    context = {
        'product': product,
        'images': product.images.all(),
        'related': related,
        'frequently_bought': frequently_bought,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
    }
    return render(request, 'shop/product_detail.html', context)

# --- Cart Views ---

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Merge session cart if it exists
        session_key = request.session.session_key
        if session_key:
            session_cart = Cart.objects.filter(session_id=session_key).first()
            if session_cart:
                for item in session_cart.items.all():
                    existing_item = CartItem.objects.filter(cart=cart, product=item.product).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item.cart = cart
                        item.save()
                session_cart.delete()
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    return cart

def cart_detail_view(request):
    cart = get_or_create_cart(request)
    store_settings = StoreSetting.get_settings()
    
    # Calculate free shipping progress bar
    subtotal = cart.total_price
    shipping_threshold = store_settings.free_shipping_threshold
    free_shipping_progress = 0
    if subtotal > 0:
        free_shipping_progress = min(int((subtotal / shipping_threshold) * 100), 100)
    amount_left_for_free_shipping = max(shipping_threshold - subtotal, 0)
    
    context = {
        'cart': cart,
        'free_shipping_progress': free_shipping_progress,
        'amount_left': amount_left_for_free_shipping,
        'threshold': shipping_threshold,
    }
    return render(request, 'shop/cart.html', context)

def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get('quantity', 1))
    
    if qty > product.stock:
        messages.error(request, f"Sorry, only {product.stock} items left in stock.")
        return redirect('shop:cart_detail')
        
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        if cart_item.quantity + qty > product.stock:
            messages.error(request, f"Cannot add more. Only {product.stock} in stock.")
            return redirect('shop:cart_detail')
        cart_item.quantity += qty
    else:
        cart_item.quantity = qty
    cart_item.save()
    
    messages.success(request, f"Added {qty} x {product.name} to your cart.")
    return redirect('shop:cart_detail')

def update_cart_view(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    qty = int(request.POST.get('quantity', 1))
    
    if qty <= 0:
        item.delete()
        messages.info(request, "Item removed from cart.")
    else:
        if qty > item.product.stock:
            messages.error(request, f"Only {item.product.stock} items in stock.")
        else:
            item.quantity = qty
            item.save()
            messages.success(request, "Cart updated.")
            
    return redirect('shop:cart_detail')

def remove_from_cart_view(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('shop:cart_detail')

# --- Wishlist ---

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def toggle_wishlist_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        wishlist_item.delete()
        added = False
        msg = f"Removed {product.name} from wishlist."
    else:
        Wishlist.objects.create(user=request.user, product=product)
        added = True
        msg = f"Added {product.name} to wishlist."
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'added': added, 'message': msg})
        
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'shop:home'))

# --- Checkout & Payments ---

@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    if cart.items_count == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('shop:cart_detail')
        
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-id')
    store_settings = StoreSetting.get_settings()
    
    subtotal = cart.total_price
    shipping = 0.00 if subtotal >= store_settings.free_shipping_threshold else float(store_settings.shipping_charge)
    
    # Handles Coupon Application
    discount = 0.00
    coupon_code = request.GET.get('coupon_code')
    coupon_obj = None
    if coupon_code:
        coupon_obj = Coupon.objects.filter(code__iexact=coupon_code.strip()).first()
        if coupon_obj and coupon_obj.is_valid(subtotal):
            discount = float(coupon_obj.calculate_discount(subtotal))
            messages.success(request, f"Coupon code '{coupon_code}' applied successfully!")
        else:
            messages.error(request, "Invalid or expired coupon code.")
            
    total = float(subtotal) + float(shipping) - float(discount)
    
    context = {
        'cart': cart,
        'addresses': addresses,
        'subtotal': subtotal,
        'shipping': shipping,
        'discount': discount,
        'coupon': coupon_obj,
        'total': total,
        'store_settings': store_settings,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def process_payment_view(request):
    """
    Sets up the order. Starts either Cash On Delivery or Razorpay gateway flow.
    """
    if request.method != 'POST':
        return redirect('shop:checkout')
        
    cart = get_or_create_cart(request)
    if cart.items_count == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('shop:cart_detail')
        
    address_id = request.POST.get('address')
    payment_method = request.POST.get('payment_method')
    coupon_code = request.POST.get('coupon_code')
    
    if not address_id:
        messages.error(request, "Please select a shipping address.")
        return redirect('shop:checkout')
        
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address_text = f"{address.full_name}\n{address.address_line1}\n{address.address_line2}\n{address.city}, {address.state} - {address.pin_code}\nMobile: {address.mobile_number}"
    
    store_settings = StoreSetting.get_settings()
    subtotal = cart.total_price
    shipping = 0.00 if subtotal >= store_settings.free_shipping_threshold else float(store_settings.shipping_charge)
    
    discount = 0.00
    coupon_obj = None
    if coupon_code:
        coupon_obj = Coupon.objects.filter(code__iexact=coupon_code).first()
        if coupon_obj and coupon_obj.is_valid(subtotal):
            discount = float(coupon_obj.calculate_discount(subtotal))
            
    total = float(subtotal) + float(shipping) - float(discount)
    
    # Create Order record (status: pending)
    order = Order.objects.create(
        user=request.user,
        shipping_address=address_text,
        subtotal=subtotal,
        shipping_charge=shipping,
        discount_amount=discount,
        coupon=coupon_obj,
        total_price=total,
        payment_method=payment_method,
        payment_status='pending',
        order_status='pending'
    )
    
    # Create OrderItems & decrement stock levels
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.get_price
        )
        # Decrement stock
        item.product.stock = max(item.product.stock - item.quantity, 0)
        item.product.save()
        
    # Clear the cart items
    cart.items.all().delete()
    
    if payment_method == 'cod':
        # Finalize cash on delivery order
        messages.success(request, f"Order placed successfully! Order ID: {order.order_number}")
        return render(request, 'shop/payment.html', {'order': order, 'is_cod': True})
        
    elif payment_method == 'razorpay':
        # Razorpay Payment Integration
        key_id = settings.RAZORPAY_KEY_ID
        key_secret = settings.RAZORPAY_KEY_SECRET
        is_mock = settings.RAZORPAY_IS_MOCK
        
        razorpay_order_id = f"rzp_order_{order.order_number}"
        
        if not is_mock:
            try:
                client = razorpay.Client(auth=(key_id, key_secret))
                rzp_order = client.order.create({
                    'amount': int(order.total_price * 100), # Razorpay amounts in Paisa
                    'currency': 'INR',
                    'receipt': order.order_number,
                    'payment_capture': '1'
                })
                razorpay_order_id = rzp_order['id']
            except Exception as e:
                # If API fails, fallback to local simulator or alert user
                messages.warning(request, "Razorpay API Connection failed. Running checkout in luxury demo mode.")
                
        order.razorpay_order_id = razorpay_order_id
        order.save()
        
        context = {
            'order': order,
            'razorpay_key': key_id,
            'amount_paisa': int(order.total_price * 100),
            'razorpay_order_id': razorpay_order_id,
            'is_mock': is_mock,
            'user': request.user
        }
        return render(request, 'shop/payment.html', context)
        
    return redirect('accounts:dashboard')

@csrf_exempt
def verify_razorpay_payment_view(request):
    """
    Handles signature verification post-checkout.
    Supports a mock handler for local sandbox testing.
    """
    if request.method == 'POST':
        # Parse params
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        order_id = data.get('order_id')
        payment_id = data.get('razorpay_payment_id')
        signature = data.get('razorpay_signature')
        is_mock_success = data.get('mock_success') == 'true'
        
        order = get_object_or_404(Order, order_number=order_id)
        
        if settings.RAZORPAY_IS_MOCK or is_mock_success:
            # Local simulator verification
            order.razorpay_payment_id = payment_id or f"pay_mock_{uuid.uuid4().hex[:10]}"
            order.razorpay_signature = signature or "sig_mock_dummy"
            order.payment_status = 'completed'
            order.order_status = 'processing'
            order.save()
            messages.success(request, f"Payment simulated successfully! Order {order.order_number} is processing.")
            return JsonResponse({'status': 'success', 'redirect_url': '/accounts/dashboard/'})
        else:
            # Live signature validation
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': order.razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            try:
                client.utility.verify_payment_signature(params_dict)
                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.payment_status = 'completed'
                order.order_status = 'processing'
                order.save()
                messages.success(request, "Payment verified successfully. Your order is processing!")
                return JsonResponse({'status': 'success', 'redirect_url': '/accounts/dashboard/'})
            except Exception as e:
                order.payment_status = 'failed'
                order.save()
                messages.error(request, "Signature verification failed. Payment was rejected.")
                return JsonResponse({'status': 'failed', 'error': str(e)})
                
    return redirect('shop:home')

# --- Leads Capture & Promo Code Generator ---

def lead_capture_view(request):
    """
    Validates name, phone, email from the popup, generates a single-use coupon, 
    and simulates sending confirmation mail.
    """
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            
            # Generate random 10% or 15% coupon
            discount_type = random.choice([10, 15])
            code_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            coupon_code = f"RARA-{discount_type}-{code_chars}"
            
            # Save Coupon in DB
            coupon = Coupon.objects.create(
                code=coupon_code,
                discount_percentage=discount_type,
                min_purchase=499.00,
                valid_from=timezone.now(),
                valid_to=timezone.now() + timezone.timedelta(days=30),
                active=True
            )
            
            lead.coupon_code = coupon_code
            lead.save()
            
            # Email Coupon to customer (outputs in terminal console backend)
            email_body = f"""
            Dear {lead.name},
            
            Thank you for registering on Rara Jewels!
            Here is your exclusive {discount_type}% discount coupon: {coupon_code}
            
            Use it on your next purchase (Minimum cart value: ₹499).
            Valid for 30 days.
            
            Explore Premium Imitation Jewelry here!
            Regards,
            Team Rara Jewels
            """
            try:
                send_mail(
                    subject="Your Exclusive Rara Jewels Discount Coupon!",
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[lead.email],
                    fail_silently=False
                )
            except Exception as e:
                # Fallback log
                print("Mail sending failed:", e)
                
            return JsonResponse({
                'status': 'success',
                'coupon': coupon_code,
                'discount': f"{discount_type}%",
                'message': 'Coupon generated and sent to email!'
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# --- Order Return & Support Views ---

@login_required
def request_return_view(request, order_id):
    """
    Submits return request logs for orders within 3 months purchase.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # 3-Month return validation check
    cutoff = timezone.now() - timezone.timedelta(days=90)
    if order.created_at < cutoff:
        messages.error(request, "This order is past the 3-month eligible return window.")
        return redirect('accounts:dashboard')
        
    if ReturnRequest.objects.filter(order=order).exists():
        messages.warning(request, "A return request has already been submitted for this order.")
        return redirect('accounts:dashboard')
        
    form = ReturnRequestForm()
    if request.method == 'POST':
        form = ReturnRequestForm(request.POST)
        if form.is_valid():
            ret = form.save(commit=False)
            ret.order = order
            ret.user = request.user
            ret.status = 'pending'
            ret.save()
            
            order.order_status = 'pending' # updates status for review
            order.save()
            
            messages.success(request, "Your return request has been submitted successfully.")
            return redirect('accounts:dashboard')
            
    return render(request, 'shop/return_request.html', {'order': order, 'form': form})

def track_order_view(request):
    """
    Allows tracking order details with shipping milestones.
    """
    order_num = request.GET.get('order_number')
    order = None
    if order_num:
        order = Order.objects.filter(order_number=order_num.strip()).prefetch_related('items__product').first()
        if not order:
            messages.error(request, "No order found with that order number.")
            
    return render(request, 'shop/order_track.html', {'order': order, 'order_number': order_num})

@login_required
def download_invoice_view(request, order_id):
    """
    Invokes reportlab PDF generator to download purchase receipt.
    """
    # If superuser is accessing, bypass ownership check.
    if request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
    pdf_data = generate_pdf_invoice(order)
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice-{order.order_number}.pdf"'
    return response

@login_required
def print_invoice_html_view(request, order_id):
    """
    Renders print-friendly layout. Calls browser window.print() on load.
    """
    if request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
    return render(request, 'shop/invoice_print.html', {'order': order})

def return_policy_view(request):
    """
    Renders the static 3-Month Return Policy informational page.
    """
    return render(request, 'shop/return_policy.html')

def faq_view(request):
    return render(request, 'faq.html')

def shipping_policy_view(request):
    return render(request, 'shipping_policy.html')

def privacy_policy_view(request):
    return render(request, 'privacy_policy.html')

def terms_view(request):
    return render(request, 'terms.html')

def contact_view(request):
    return render(request, 'contact.html')

def about_view(request):
    return render(request, 'about.html')

def blogs_view(request):
    return render(request, 'blogs.html')

def careers_view(request):
    return render(request, 'careers.html')
    from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

