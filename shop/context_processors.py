from .models import Category, Cart, Wishlist, StoreSetting
from django.utils import timezone

def store_context(request):
    # Retrieve all parent categories with prefetch on subcategories
    parent_categories = Category.objects.filter(parent=None).prefetch_related('subcategories')
    
    # Calculate cart count
    cart_items_count = 0
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_id=session_key).first()
            
    if cart:
        cart_items_count = cart.items_count

    # Calculate wishlist count
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    # Get global store settings
    settings_obj = StoreSetting.get_settings()

    return {
        'nav_categories': parent_categories,
        'cart_count': cart_items_count,
        'wishlist_count': wishlist_count,
        'store_settings': settings_obj,
        'current_year': timezone.now().year
    }
