from rest_framework import serializers
from django.contrib.auth.models import Group

from . import models


class ChangePwdSerializer(serializers.Serializer):
    """修改密码"""
    password = serializers.CharField(label='原密码', max_length=128)
    new_password = serializers.CharField(label='新密码', max_length=128)

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError("原密码不正确")
        return value

    def save(self, **kwargs):
        self.instance.set_password(self.initial_data.get('new_password'))
        self.instance.save()
        return self.instance


class UserSerializer(serializers.ModelSerializer):
    """用户"""
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = models.User
        fields = (
            'pk',
            'username',
            'is_superuser',
            'last_login',
            'full_name',
            'email',
            'phone',
            'mobile',
            'sex',
            'marital_status',
            'home_address',
            'birthplace',
            'birthday',
            'nationality',
            'political_status',
            'educational_level',
            'is_staff',
            'is_active',
            'date_joined',
            'department',
            'department_name',
            'employee_position',
            'employee_rank',
            'description',
            'groups',
        )


class GroupUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            'pk',
            'username',
            'full_name'
        )


class GroupSerializer(serializers.ModelSerializer):
    """权限组"""
    user = GroupUserSerializer(source='user_set', many=True, read_only=True)

    class Meta:
        model = Group
        fields = (
            'pk',
            'name',
            'user'
        )


class DepartmentSerializer(serializers.ModelSerializer):
    """机构部门"""
    items = serializers.SerializerMethodField()
    expand = serializers.SerializerMethodField()

    class Meta:
        model = models.Department
        fields = (
            'pk',
            'name',
            'parent',
            'category',
            'contact_name',
            'contact_phone',
            'contact_mobile',
            'contact_fax',
            'description',
            'items',
            'expand',
        )

    def get_items(self, obj):
        children = obj.children.all()
        childrens = DepartmentSerializer(children, many=True).data
        result = []
        result.extend(childrens)
        return result

    def get_expand(self, obj):
        return obj.is_root_node()


class FlatDepartmentSerializer(serializers.ModelSerializer):
    """机构部门"""

    class Meta:
        model = models.Department
        fields = (
            'pk',
            'name',
            'parent',
            'category',
            'contact_name',
            'contact_phone',
            'contact_mobile',
            'contact_fax',
            'description',
        )


class UserDepChangeSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = models.UserDepChange
        fields = (
            'user',
            'old_department',
            'new_department',
            'create_time'
        )
