from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات اضافی', {
            'fields': ('phone_number', 'date_of_birth', 'avatar')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات اضافی', {
            'fields': ('phone_number', 'date_of_birth', 'avatar')
        }),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')