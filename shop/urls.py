from django.urls import path
from . import views
from . import admin_views


app_name = 'shop'

urlpatterns = [
    # Front-end Storefront
    path('', views.home_view, name='home'),
    path('products/', views.category_products_view, name='products'),
    path('products/category/<slug:slug>/', views.category_products_view, name='category_products'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),

    path(
        'payment-success/<str:order_number>/',
        views.payment_success_view,
        name='payment_success',
    ),  
    
    # Cart
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_view, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist_view, name='toggle_wishlist'),

   
    
    # Checkout & Payment
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/pay/', views.process_payment_view, name='process_payment'),
    path('checkout/verify/', views.verify_razorpay_payment_view, name='verify_payment'),
    
    # Discount popup capture
    path('lead/capture/', views.lead_capture_view, name='lead_capture'),
    
    # Order Tracking, Returns, and Invoice prints
    path('order/track/', views.track_order_view, name='track_order'),
    path('order/<int:order_id>/return/', views.request_return_view, name='request_return'),
    path('order/<int:order_id>/invoice/download/', views.download_invoice_view, name='download_invoice'),
    path('order/<int:order_id>/invoice/print/', views.print_invoice_html_view, name='print_invoice_html'),
    path('return-policy/', views.return_policy_view, name='return_policy'),

    # Static Pages
    path('faq/', views.faq_view, name='faq'),
    path('shipping-policy/', views.shipping_policy_view, name='shipping_policy'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_view, name='terms'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('blogs/', views.blogs_view, name='blogs'),
    path('careers/', views.careers_view, name='careers'), 

    # --- Custom Luxury Admin Dashboard ---
    path('luxury-admin/', admin_views.admin_dashboard_view, name='admin_dashboard'),
    
    # Products CRUD
    path('luxury-admin/products/', admin_views.admin_products_view, name='admin_products'),
    path('luxury-admin/product/add/', admin_views.admin_product_create_view, name='admin_product_create'),
    path('luxury-admin/product/<int:pk>/edit/', admin_views.admin_product_update_view, name='admin_product_update'),
    path('luxury-admin/product/<int:pk>/delete/', admin_views.admin_product_delete_view, name='admin_product_delete'),
    
    # Categories CRUD
    path('luxury-admin/categories/', admin_views.admin_categories_view, name='admin_categories'),
    path('luxury-admin/category/add/', admin_views.admin_category_create_view, name='admin_category_create'),
    path('luxury-admin/category/<int:pk>/edit/', admin_views.admin_category_update_view, name='admin_category_update'),
    path('luxury-admin/category/<int:pk>/delete/', admin_views.admin_category_delete_view, name='admin_category_delete'),
    
    # Orders Management
    path('luxury-admin/orders/', admin_views.admin_orders_view, name='admin_orders'),
    path('luxury-admin/order/<str:order_number>/', admin_views.admin_order_detail_view, name='admin_order_detail'),
    path('luxury-admin/order/<str:order_number>/delete/',admin_views.admin_order_delete_view,name='admin_order_delete'),
    
    # Returns Management
    path('luxury-admin/returns/', admin_views.admin_return_requests_view, name='admin_returns'),
    path('luxury-admin/return/<int:pk>/action/', admin_views.admin_return_request_action_view, name='admin_return_action'),
    
    # Coupons Management
    path('luxury-admin/coupons/', admin_views.admin_coupons_view, name='admin_coupons'),
    path('luxury-admin/coupon/<int:pk>/delete/', admin_views.admin_coupon_delete_view, name='admin_coupon_delete'),
    
    # Offers Management
    path('luxury-admin/offers/', admin_views.admin_offers_view, name='admin_offers'),
    path('luxury-admin/offer/<int:pk>/delete/', admin_views.admin_offer_delete_view, name='admin_offer_delete'),
    
    # Banner Management
    path('luxury-admin/banners/', admin_views.admin_banners_view, name='admin_banners'),
    path('luxury-admin/banner/<int:pk>/delete/', admin_views.admin_banner_delete_view, name='admin_banner_delete'),
    
    # Store settings
    path('luxury-admin/settings/', admin_views.admin_settings_view, name='admin_settings'),
    
    # Reports
    path('luxury-admin/reports/', admin_views.admin_reports_view, name='admin_reports'),
    path('luxury-admin/reports/excel/', admin_views.admin_export_excel_view, name='admin_export_excel'),
    path('luxury-admin/reports/pdf/', admin_views.admin_export_pdf_view, name='admin_export_pdf'),
]
