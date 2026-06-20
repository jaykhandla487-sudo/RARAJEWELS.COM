from django import forms
from .models import ProductReview, ReturnRequest, CustomerDiscountLead, Coupon, StoreSetting, Product, Category, Banner, Offer

class ProductReviewForm(forms.ModelForm):
    review_image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={
        'class': 'form-control bg-dark text-light border-gold',
        'accept': 'image/*'
    }))

    class Meta:
        model = ProductReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Stars") for i in range(5, 0, -1)], attrs={
                'class': 'form-select bg-dark text-light border-gold'
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light border-gold',
                'rows': 4,
                'placeholder': 'Write your honest review here...'
            }),
        }

class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light border-gold',
                'rows': 4,
                'placeholder': 'Please specify the reason for return (e.g. size issues, damaged product, incorrect item)...'
            })
        }

class LeadForm(forms.ModelForm):
    class Meta:
        model = CustomerDiscountLead
        fields = ['name', 'mobile', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'Your Full Name', 'required': 'true'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': '10-digit Mobile Number', 'required': 'true'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'Your Email Address', 'required': 'true'}),
        }

class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control bg-dark text-light border-gold',
        'placeholder': 'Enter Promo Code'
    }))

# Admin management forms
class ProductForm(forms.ModelForm):
    primary_image = forms.ImageField(required=False, label="Primary Image", widget=forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-light border-gold'}))
    extra_image_1 = forms.ImageField(required=False, label="Gallery Image 1", widget=forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-light border-gold'}))
    extra_image_2 = forms.ImageField(required=False, label="Gallery Image 2", widget=forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-light border-gold'}))

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount_price', 'category', 'stock', 'is_featured', 'is_new_arrival', 'is_best_seller', 'is_trending']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-dark text-light border-gold', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'category': forms.Select(attrs={'class': 'form-select bg-dark text-light border-gold'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input bg-dark border-gold'}),
            'is_new_arrival': forms.CheckboxInput(attrs={'class': 'form-check-input bg-dark border-gold'}),
            'is_best_seller': forms.CheckboxInput(attrs={'class': 'form-check-input bg-dark border-gold'}),
            'is_trending': forms.CheckboxInput(attrs={'class': 'form-check-input bg-dark border-gold'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'parent': forms.Select(attrs={'class': 'form-select bg-dark text-light border-gold'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-dark text-light border-gold', 'rows': 3}),
        }

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'discount_amount', 'min_purchase', 'valid_from', 'valid_to', 'active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'min_purchase': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'type': 'datetime-local'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input bg-dark border-gold'}),
        }

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['title', 'offer_type', 'discount_percentage', 'discount_amount', 'buy_product', 'get_product', 'banner_image', 'start_time', 'end_time', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'offer_type': forms.Select(attrs={'class': 'form-select bg-dark text-light border-gold'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'buy_product': forms.Select(attrs={'class': 'form-select bg-dark text-light border-gold'}),
            'get_product': forms.Select(attrs={'class': 'form-select bg-dark text-light border-gold'}),
            'banner_image': forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'type': 'datetime-local'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input bg-dark border-gold'}),
        }

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'image', 'link_url', 'order', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'link_url': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'order': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input bg-dark border-gold'}),
        }

class StoreSettingForm(forms.ModelForm):
    class Meta:
        model = StoreSetting
        fields = ['free_shipping_threshold', 'shipping_charge', 'whatsapp_number', 'instagram_url', 'facebook_url', 'youtube_url', 'announcement_text']
        widgets = {
            'free_shipping_threshold': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'shipping_charge': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'instagram_url': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'facebook_url': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'youtube_url': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'announcement_text': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
        }
