from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address

class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'name', 'mobile', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name', 'mobile')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'mobile')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'mobile', 'password'),
        }),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Address)
