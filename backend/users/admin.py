from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'phone', 'role', 'is_phone_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_phone_verified', 'is_active']
    search_fields = ['email', 'phone', 'first_name', 'last_name']
    ordering = ['-date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('phone', 'role', 'is_phone_verified', 'whatsapp_opt_in')}),
    )
