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
            'readed_licence',
            'sort_num',
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


class DepartmentMoveSerializer(serializers.Serializer):
    POSITION_CHOICES = (
        ('first-child', '第一个子部门'),
        ('last-child', '最后一个子部门'),
        ('left', '之前'),
        ('right', '之后'),
    )
    department = serializers.IntegerField(
        label='当前部门ID',
        help_text='当前部门ID'
    )
    target = serializers.IntegerField(
        label='目标部门ID',
        help_text='目标部门ID'
    )
    position = serializers.ChoiceField(
        label='位置',
        help_text='位置',
        choices=POSITION_CHOICES
    )

    def update(self, instance, validated_data):
        target = models.Department.objects.get(pk=validated_data['target'])
        instance.move_to(target, validated_data['position'])
        return instance

    def create(self, validated_data):
        department = models.Department.objects.get(pk=validated_data['department'])
        target = models.Department.objects.get(pk=validated_data['target'])
        department.move_to(target, validated_data['position'])
        return department


class UserOrderSerializer(serializers.Serializer):
    USER_POSITION_CHOICES = (
        ('left', '之前'),
        ('right', '之后'),
    )
    user = serializers.IntegerField(
        label='当前用户ID',
        help_text='当前用户ID'
    )
    target = serializers.IntegerField(
        label='目标用户ID',
        help_text='目标用户ID'
    )
    position = serializers.ChoiceField(
        label='位置',
        help_text='位置',
        choices=USER_POSITION_CHOICES
    )

    def update(self, instance, validated_data):
        target = models.User.objects.get(pk=validated_data['target'])
        instance.move_to(target, validated_data['position'])
        return instance

    def create(self, validated_data):
        user = models.User.objects.get(pk=validated_data['user'])
        target = models.User.objects.get(pk=validated_data['target'])
        user.move_to(target, validated_data['position'])
        return user
