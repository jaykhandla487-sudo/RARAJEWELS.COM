from django.contrib import admin
from .models import (
    Product, Category, ProductImage, Cart, CartItem, Coupon, 
    Offer, CustomerDiscountLead, Order, OrderItem, ReturnRequest, 
    Banner, Wishlist, ProductReview, ReviewImage, StoreSetting
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'stock', 'category', 'is_featured', 'is_new_arrival', 'is_best_seller')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    search_fields = ('name', 'description')
    list_filter = ('category', 'is_featured', 'is_new_arrival', 'is_best_seller', 'is_trending')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_price', 'payment_method', 'payment_status', 'order_status', 'created_at')
    list_filter = ('payment_method', 'payment_status', 'order_status', 'created_at')
    search_fields = ('order_number', 'user__email', 'shipping_address')
    inlines = [OrderItemInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon)
admin.site.register(Offer)
admin.site.register(CustomerDiscountLead)
admin.site.register(ReturnRequest)
admin.site.register(Banner)
admin.site.register(Wishlist)
admin.site.register(ProductReview)
admin.site.register(ReviewImage)
admin.site.register(StoreSetting)
