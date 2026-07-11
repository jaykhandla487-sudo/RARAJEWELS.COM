from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
import uuid
from django.urls import reverse

class StoreSetting(models.Model):
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=699.00)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=59.00)
    whatsapp_number = models.CharField(max_length=20, default='+917777974101')
    instagram_url = models.CharField(max_length=255, default='https://instagram.com/rarajewels')
    facebook_url = models.CharField(max_length=255, default='https://facebook.com/rarajewels')
    youtube_url = models.CharField(max_length=255, default='https://youtube.com/rarajewels')
    announcement_text = models.CharField(max_length=255, default='Free Shipping Above ₹699')

    def __str__(self):
        return "Global Store Settings"

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Check unique slug
            original_slug = self.slug
            count = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
        
    def get_absolute_url(self):
        return reverse(
            "shop:category_products",
            kwargs={"slug": self.slug}
        )   

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=True)
    is_best_seller = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            count = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "shop:product_detail",
            kwargs={"slug": self.slug}
        )   

    @property
    def get_price(self):
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def discount_percent(self):
        if self.discount_price and self.price > 0:
            diff = self.price - self.discount_price
            return int((diff / self.price) * 100)
        return 0

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()

        if primary:
            return primary.image.url

        first = self.images.first()

        if first:
            return first.image.url
        return "/static/images/product-placeholder.jpg"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} Image"

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} ({self.user.email if self.user else 'Guest'})"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.get_price * self.quantity

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self, cart_total):
        now = timezone.now()
        if not self.active:
            return False
        if not (self.valid_from <= now <= self.valid_to):
            return False
        if cart_total < self.min_purchase:
            return False
        return True

    def calculate_discount(self, cart_total):
        if not self.is_valid(cart_total):
            return 0
        if self.discount_percentage:
            return (self.discount_percentage / 100) * cart_total
        if self.discount_amount:
            return min(self.discount_amount, cart_total)
        return 0

class Offer(models.Model):
    OFFER_TYPES = [
        ('sale', 'Sale Offer'),
        ('flash', 'Flash Sale'),
        ('bogo', 'Buy One Get One'),
        ('combo', 'Combo Offer'),
        ('percent', 'Percentage Discount'),
        ('fixed', 'Fixed Discount'),
        ('festival', 'Festival Offer'),
        ('limited_time', 'Limited Time Offer')
    ]
    title = models.CharField(max_length=200)
    offer_type = models.CharField(max_length=30, choices=OFFER_TYPES)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    buy_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='bogo_buy')
    get_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='bogo_get')
    banner_image = models.ImageField(upload_to='offers/', null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.get_offer_type_display()})"

    def is_currently_active(self):
        now = timezone.now()
        return self.active and (self.start_time <= now <= self.end_time)

class CustomerDiscountLead(models.Model):
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    coupon_code = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned')
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=100, unique=True)
    shipping_address = models.TextField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('cod', 'Cash On Delivery'), ('razorpay', 'Razorpay')])
    payment_status = models.CharField(max_length=20, default='pending', choices=PAYMENT_STATUS_CHOICES)
    order_status = models.CharField(max_length=20, default='pending', choices=ORDER_STATUS_CHOICES)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = 'RARA-' + str(uuid.uuid4().hex[:10]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.order_number})"

    @property
    def subtotal(self):
        return self.price * self.quantity

class ReturnRequest(models.Model):
    RETURN_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('refunded', 'Refunded')
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pending', choices=RETURN_STATUS_CHOICES)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return Request for {self.order.order_number}"

class Banner(models.Model):
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to='banners/')
    desktop_image = models.ImageField(
    upload_to='banners/',
    blank=True,
    null=True
)

    mobile_image = models.ImageField(
        upload_to='banners/',
        blank=True,
        null=True
    )
    link_url = models.CharField(max_length=255, blank=True)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title or f"Banner {self.id}"

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review ({self.rating} stars) by {self.user.name} on {self.product.name}"

class ReviewImage(models.Model):
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/')

    def __str__(self):
        return f"Review image for {self.review.id}"
