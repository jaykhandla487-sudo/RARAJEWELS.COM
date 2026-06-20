from django import forms
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control bg-dark text-light border-gold',
        'placeholder': 'Enter your password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control bg-dark text-light border-gold',
        'placeholder': 'Confirm your password'
    }))

    class Meta:
        model = User
        fields = ['name', 'mobile', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'Enter your full name'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'Enter your mobile number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'Enter your email address'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control bg-dark text-light border-gold',
        'placeholder': 'Enter your email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control bg-dark text-light border-gold',
        'placeholder': 'Enter your password'
    }))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'mobile']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'mobile_number', 'address_line1', 'address_line2', 'city', 'state', 'pin_code', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'Full Name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': '10-digit Mobile Number'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'Flat, House no., Building, Company, Apartment'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'Area, Street, Sector, Village'}),
            'city': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'Town/City'}),
            'state': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': 'State'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-gold', 'placeholder': '6-digit PIN Code'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input bg-dark border-gold'}),
        }
