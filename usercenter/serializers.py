from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class GroupUserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = models.User
        fields = (
            'pk',
            'username',
            'full_name',
            'department_name',
        )


class FuncPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FuncPermission
        fields = (
            'pk',
            'name',
            'codename',
        )


class FuncGroupSerializer(serializers.ModelSerializer):
    """权限组"""
    user = GroupUserSerializer(source='user_set', many=True, read_only=True)
    permissions_name = serializers.SerializerMethodField()

    class Meta:
        model = models.FuncGroup
        fields = (
            'pk',
            'name',
            'user',
            'permissions',
            'permissions_name',
        )

    def get_permissions_name(self, obj):
        return list(obj.permissions.all().values_list('name', flat=True))


class FuncGroupMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FuncGroup
        fields = (
            'pk',
            'name',
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
            'fdeptid',
            'items',
            'expand',
            'open_time',
            'close_time',
        )

    def get_items(self, obj):
        children = obj.children.all()
        childrens = DepartmentSerializer(children, many=True).data
        result = []
        result.extend(childrens)
        return result

    def get_expand(self, obj):
        return obj.is_root_node()


class DepartmentMiniSerializer(serializers.ModelSerializer):
    """机构部门简要信息"""
    items = serializers.SerializerMethodField()
    leaf = serializers.SerializerMethodField()

    class Meta:
        model = models.Department
        fields = (
            'pk',
            'name',
            'parent',
            'category',
            'items',
            'leaf',
            'fdeptid',
        )

    def get_items(self, obj):
        children = obj.children.all()
        childrens = DepartmentMiniSerializer(children, many=True).data
        result = []
        result.extend(childrens)
        if len(result) == 0:
            return None
        return result

    def get_leaf(self, obj):
        return not obj.children.all()


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
            'fdeptid',
            'open_time',
            'close_time',
        )


class UserSerializer(serializers.ModelSerializer):
    """用户"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_info = FlatDepartmentSerializer(source='department', read_only=True)
    joinrequest = serializers.SerializerMethodField()

    # group_names = serializers.SerializerMethodField()
    # mydepartments = serializers.SerializerMethodField(help_text='我所有的门店')

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
            'department_info',
            'employee_position',
            'employee_rank',
            'description',
            # 'groups',
            # 'group_names',
            'func_names',
            'func_codenames',
            'func_groups',
            'func_group_names',
            'readed_licence',
            'fuid',
            'category',
            'category_names',
            'sort_num',
            'pid',
            'join_date',
            'out_date',
            # 'mydepartments',
            'wechart_oid',
            'number_01',  # 工时费用
            'number_02',  # 工作年限
            'number_03', 'number_04', 'number_05',
            'field_01', 'field_02', 'field_03', 'field_04',
            'field_05',  # 个人评价
            'fujian_01', 'fujian_02', 'fujian_03', 'fujian_04', 'fujian_05',
            'fujian_06', 'fujian_07', 'fujian_08', 'fujian_09',
            'fujian_10',
            'joinrequest',
        )

    def get_joinrequest(self, obj):
        try:
            return UserRequireSerializer(models.UserRequire.objects.get(target_user=obj)).data
        except models.UserRequire.DoesNotExist:
            return None


class UserMinSerializer(serializers.ModelSerializer):
    """用户"""
    department_name = serializers.SerializerMethodField()

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
            'func_names',
            'func_codenames',
            'func_group_names',
            'readed_licence',
            'sort_num',
            'pid',
            'join_date',
            'out_date',
            'wechart_oid',
            'fuid',
            'category',
            'category_names',
            'number_01',  # 工时费用
            'number_02',  # 工作年限
            'number_03', 'number_04', 'number_05',
            'field_01', 'field_02', 'field_03', 'field_04',
            'field_05',  # 个人评价
            'fujian_01', 'fujian_02', 'fujian_03', 'fujian_04', 'fujian_05',
            'fujian_06', 'fujian_07', 'fujian_08', 'fujian_09',
            'fujian_10',
        )

    def get_department_name(self, obj):
        return obj.department.name if obj.department else ''


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


class UserLoginLogSerializer(serializers.ModelSerializer):
    user_info = UserMinSerializer(source='user', read_only=True)

    class Meta:
        model = models.UserLoginLog
        fields = (
            'user',
            'user_info',
            'username',
            'full_name',
            'login_time',
            'ipaddress',
            'login_type',
        )


class UserRequireSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserRequire
        fields = (
            'pk',
            'phone',
            'full_name',
            'group',
            'group_display',
            'department',
            'department_display',
            'audit_user',
            'audit_time',
            'state',
            'create_time',
            'denial_reason',
            'create_time_display',
            'category',
            'category_names',
            'field_01',
            'field_02',
            'field_03',
            'field_04',
            'field_05',
            'fujian_01',
            'fujian_02',
            'fujian_03',
            'fujian_04',
            'fujian_05',
            'fujian_06',
            'fujian_07',
            'fujian_08',
            'fujian_09',
            'fujian_10',
        )


class UserRequireCreateSerializer(serializers.ModelSerializer):
    phone_access = serializers.CharField(required=True, help_text='验证码')

    class Meta:
        model = models.UserRequire
        fields = (
            'phone',
            'phone_access',
            'full_name',
            'group',
            'password',
            'category',
            'category_names',
            # 'department',
            'field_01',
            'field_02',
            'field_03',
            'field_04',
            'field_05',
            'fujian_01',
            'fujian_02',
            'fujian_03',
            'fujian_04',
            'fujian_05',
            'fujian_06',
            'fujian_07',
            'fujian_08',
            'fujian_09',
            'fujian_10',
        )

    def validate_phone(self, value):
        if models.UserRequire.objects.filter(phone=value).exclude(state='未通过'):
            raise ValidationError('申请已存在，请勿重复发送！')
        return value

    # def validate(self, data):
    #     phone, pa = data['phone'], data['phone_access']
    #     try:
    #         models.PhoneAccess.objects.get(phone=phone, phone_access=pa)
    #     except models.PhoneAccess.DoesNotExist:
    #         raise ValidationError('验证码错误')
    #     return data


class UserRequirePassSerializer(UserRequireSerializer):

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if instance.state == '已同意':
            try:
                instance.create_user()
            except ValueError:
                pass
        return instance


class LeaveRequireSerializer(serializers.ModelSerializer):
    user_info = GroupUserSerializer(source='user', read_only=True)

    class Meta:
        model = models.LeaveRequire
        fields = (
            'pk',
            'user',
            'user_info',
            'leave_reason',
            'leave_date',
            'denial_reason',
            'state',
            'audit_user',
            'audit_time',
            'create_time',
        )


class LeaveRequirePassSerializer(LeaveRequireSerializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if instance.state == '已同意' and instance.user.is_active:
            user = instance.user
            user.is_active = False
            user.save()
            user.customer_set.update(beautician=None)
        return instance
