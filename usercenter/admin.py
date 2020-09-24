from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django_mptt_admin.admin import DjangoMpttAdmin
from . import models

try:
    admin.site.unregister(Group)
except:
    pass

@admin.register(models.User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'full_name', 'department', 'employee_position', 'is_active', 'is_superuser']
    search_fields = ('username', 'full_name', 'email', 'mobile',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('department', 'full_name', 'mobile', 'phone', 'employee_position', 'email', )}),
        # ('模型权限', {
        #     'fields': ('groups', 'user_permissions', ),
        # }),
        ('功能权限', {
            'fields': ('func_groups', 'func_user_permissions', ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', )}),
        ('用户状态', {
            'fields': ('is_active', 'is_staff', 'is_superuser', ),
        }),
        ('微信信息', {'fields': ('wechart_name', 'wechart_avatar', 'wechart_oid', 'wechart_uid', )}),
    )
    filter_horizontal = ('groups', 'user_permissions', 'func_groups', 'func_user_permissions', )
    # list_filter = ['is_manager', 'is_publisher', 'is_reviewer']


@admin.register(models.Department)
class DepartmentAdmin(DjangoMpttAdmin):
    list_display = ['name', 'parent', ]
    exclude = ['category', 'open_time', 'close_time']


@admin.register(models.UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'ipaddress', 'login_time']
    readonly_fields = ['username', 'full_name', 'ipaddress', 'login_time', 'user']


@admin.register(models.UserRequire)
class UserRequireAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'department', 'phone', 'group']


@admin.register(models.LeaveRequire)
class LeaveRequireAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'leave_reason',
        'leave_date',
        'state',
        'create_time',
    ]


@admin.register(models.FuncGroup)
class FuncGroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)


@admin.register(models.FuncPermission)
class FuncPermissionAdmin(admin.ModelAdmin):
    search_fields = ('name', 'codename',)
    ordering = ('codename',)


@admin.register(models.PhoneAccess)
class PhoneAccessAdmin(admin.ModelAdmin):
    list_display = ['create_time', 'phone', 'phone_access',]
    ordering = ('-create_time',)
