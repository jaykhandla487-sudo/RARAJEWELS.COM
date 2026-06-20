from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('address/delete/<int:address_id>/', views.delete_address_view, name='delete_address'),
    path('address/default/<int:address_id>/', views.set_default_address_view, name='set_default_address'),
]
