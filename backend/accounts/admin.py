from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'is_email_verified', 'profile_completed', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_email_verified', 'profile_completed', 'is_staff', 'is_active', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Profile Status'), {'fields': ('is_email_verified', 'profile_completed')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    actions = ['verify_email', 'mark_profile_completed']

    def verify_email(self, request, queryset):
        queryset.update(is_email_verified=True)
    verify_email.short_description = "Mark selected users as email verified"

    def mark_profile_completed(self, request, queryset):
        queryset.update(profile_completed=True)
    mark_profile_completed.short_description = "Mark selected users as profile completed"