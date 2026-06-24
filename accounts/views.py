from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import SignupForm, LoginForm, ProfileForm, AddressForm
from .models import Address

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            auth_login(request, user)
            messages.success(request, f"Welcome to Rara Jewels, {user.name}!")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.name}!")
                if next_url:
                    return redirect(next_url)
                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid input data.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('shop:home')

@login_required
def dashboard_view(request):
    # Fetch user orders, wishlist, addresses
    # Import locally to avoid circular dependencies
    from shop.models import Order, Wishlist
    
    orders = Order.objects.filter(user=request.user).order_add_time_desc() if hasattr(Order.objects, 'order_add_time_desc') else Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-id')
    
    profile_form = ProfileForm(instance=request.user)
    address_form = AddressForm()
    
    active_tab = request.GET.get('tab', 'orders')
    
    # Handle forms if submitted on dashboard
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('shop:checkout')
            active_tab = 'profile'
        elif action == 'add_address':
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()
                messages.success(request, "Address saved successfully.")
                return redirect('shop:checkout')
            active_tab = 'addresses'
            
    context = {
        'orders': orders,
        'wishlist_items': wishlist_items,
        'addresses': addresses,
        'profile_form': profile_form,
        'address_form': address_form,
        'active_tab': active_tab,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def delete_address_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect(reverse('accounts:dashboard') + '?tab=addresses')

@login_required
def set_default_address_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, "Default address updated.")
    return redirect(reverse('accounts:dashboard') + '?tab=addresses')
