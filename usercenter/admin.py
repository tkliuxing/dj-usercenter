from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from mptt.admin import MPTTModelAdmin
from . import models


@admin.register(models.User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'full_name', 'department', 'employee_position', 'is_active', 'is_superuser']
    search_fields = ('username', 'full_name', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'mobile', 'phone', 'employee_position', 'email', )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'department'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # list_filter = ['is_manager', 'is_publisher', 'is_reviewer']


@admin.register(models.Department)
class DepartmentAdmin(MPTTModelAdmin):
    list_display = ['name', 'parent', 'category', ]
