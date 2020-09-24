import datetime
import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    UnicodeUsernameValidator,
    timezone,
    send_mail,
)
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# 功能权限
class FuncPermission(models.Model):
    name = models.CharField('名称', max_length=255)
    codename = models.CharField('代码', max_length=100, unique=True)

    class Meta:
        verbose_name = '04.功能权限'
        verbose_name_plural = verbose_name
        ordering = ('codename',)

    def __str__(self):
        return "%s | %s" % (
            self.name,
            self.codename
        )


# 角色
class FuncGroup(models.Model):
    name = models.CharField('角色名称', max_length=150, unique=True)
    permissions = models.ManyToManyField(
        FuncPermission,
        verbose_name='功能权限',
        blank=True,
    )

    class Meta:
        verbose_name = '03.角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 用户控制器
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, password, **extra_fields)


# 用户模型
class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        '用户名', max_length=150, unique=True,
        help_text='必填，小于150个字符。',
        validators=[username_validator],
        error_messages={'unique': "用户名已存在。"},
    )
    full_name = models.CharField('姓名', max_length=30, blank=True, help_text='姓名')
    email = models.EmailField('Email', null=True, blank=True, help_text='Email')
    mobile = models.CharField('手机号码', max_length=32, null=True, blank=True, help_text='手机号码')
    phone = models.CharField('办公电话', max_length=32, null=True, blank=True, help_text='办公电话')
    is_staff = models.BooleanField('可进入后台管理', default=False, help_text='可进入后台管理')
    is_active = models.BooleanField('允许登录', default=True, help_text='允许登录')
    date_joined = models.DateTimeField('创建时间', default=timezone.now, help_text='创建时间')
    inner_code = models.CharField('内部工号', max_length=32, null=True, blank=True, help_text='内部工号')
    employee_position = models.CharField('职务', max_length=32, null=True, blank=True, help_text='职务')
    employee_rank = models.CharField('职级', help_text='职级', max_length=32, null=True, blank=True)
    sex = models.CharField('性别', max_length=2, choices=(('男', '男'), ('女', '女'),), null=True, blank=True, help_text='性别')
    marital_status = models.CharField('婚姻状况', help_text='婚姻状况', null=True, blank=True,
                                      max_length=5, choices=(('已婚', '已婚'), ('未婚', '未婚'),))
    home_address = models.CharField('家庭住址', help_text='家庭住址', max_length=200, null=True, blank=True)
    birthplace = models.CharField('籍贯', help_text='籍贯', max_length=100, null=True, blank=True)
    birthday = models.DateField('出生年月日', help_text='出生年月日', null=True, blank=True)
    nationality = models.CharField('民族', help_text='民族', max_length=20, null=True, blank=True)
    political_status = models.CharField('政治面貌', help_text='政治面貌', max_length=50, blank=True, null=True)
    educational_level = models.CharField('文化程度', help_text='文化程度', max_length=20, blank=True, null=True)
    pid = models.CharField('身份证号', help_text='身份证号', max_length=20, blank=True, null=True)
    join_date = models.DateField('入职时间', null=True, blank=True, help_text='入职时间')
    out_date = models.DateField('离职时间', null=True, blank=True, help_text='离职时间')
    description = models.TextField('备注', null=True, blank=True, help_text='备注')
    department = models.ForeignKey('Department', null=True, blank=True, related_name='users',
                                   on_delete=models.SET_NULL, verbose_name='部门', help_text='部门')
    sort_num = models.IntegerField('排序编号', help_text='排序编号', null=True, blank=True, default=0, db_index=True)
    readed_licence = models.BooleanField('已阅读用户协议', help_text='已阅读用户协议', default=False, null=True, blank=True)

    fuid = models.IntegerField('金蝶K3系统ID', null=True, blank=True, help_text='金蝶K3系统ID（FItemID）')

    category = models.ManyToManyField(
        'baseconfig.BaseConfigItem', blank=True, verbose_name='分类', help_text='分类', related_name='users'
    )

    # 微信相关
    wechart_name = models.CharField('微信名称', max_length=64, null=True, blank=True, db_index=True, help_text='微信名称')
    wechart_avatar = models.ImageField('微信头像', upload_to='avatar/%Y/%m/%d/', null=True, blank=True, help_text='微信头像')
    wechart_oid = models.CharField('微信OID', max_length=64, null=True, blank=True, db_index=True, help_text='微信OID')
    wechart_uid = models.CharField('微信UID', max_length=64, null=True, blank=True, db_index=True, help_text='微信UID')
    wechart_access_token = models.CharField(
        '微信 ACCESS TOKEN', max_length=128, null=True, blank=True, help_text='微信 ACCESS TOKEN'
    )
    wechart_refresh_token = models.CharField(
        '微信 REFRESH TOKEN', max_length=128, null=True, blank=True, help_text='微信 REFRESH TOKEN'
    )
    wechart_session_key = models.CharField(
        '微信会话密钥 SESSION_KEY', max_length=255, null=True, blank=True, help_text='微信会话密钥 SESSION_KEY'
    )

    func_groups = models.ManyToManyField(
        FuncGroup,
        verbose_name='角色',
        blank=True,
        help_text='角色',
        related_name="user_set",
        related_query_name="user",
    )
    func_user_permissions = models.ManyToManyField(
        FuncPermission,
        verbose_name='功能权限',
        blank=True,
        help_text='功能权限',
        related_name="user_set",
        related_query_name="user",
    )

    number_01 = models.FloatField('数值内容01', null=True, blank=True, help_text='数值内容01')
    number_02 = models.FloatField('数值内容02', null=True, blank=True, help_text='数值内容02')
    number_03 = models.FloatField('数值内容03', null=True, blank=True, help_text='数值内容03')
    number_04 = models.FloatField('数值内容04', null=True, blank=True, help_text='数值内容04')
    number_05 = models.FloatField('数值内容05', null=True, blank=True, help_text='数值内容05')

    field_01 = models.TextField('附加内容01', null=True, blank=True, help_text='附加内容01')
    field_02 = models.TextField('附加内容02', null=True, blank=True, help_text='附加内容02')
    field_03 = models.TextField('附加内容03', null=True, blank=True, help_text='附加内容03')
    field_04 = models.TextField('附加内容04', null=True, blank=True, help_text='附加内容04')
    field_05 = models.TextField('附加内容05', null=True, blank=True, help_text='附加内容05')

    fujian_01 = models.FileField(
        '附件01', null=True, blank=True, help_text='附件01', upload_to='user/%Y/%m/%d/'
    )
    fujian_02 = models.FileField(
        '附件02', null=True, blank=True, help_text='附件02', upload_to='user/%Y/%m/%d/'
    )
    fujian_03 = models.FileField(
        '附件03', null=True, blank=True, help_text='附件03', upload_to='user/%Y/%m/%d/'
    )
    fujian_04 = models.FileField(
        '附件04', null=True, blank=True, help_text='附件04', upload_to='user/%Y/%m/%d/'
    )
    fujian_05 = models.FileField(
        '附件05', null=True, blank=True, help_text='附件05', upload_to='user/%Y/%m/%d/'
    )
    fujian_06 = models.FileField(
        '附件06', null=True, blank=True, help_text='附件06', upload_to='user/%Y/%m/%d/'
    )
    fujian_07 = models.FileField(
        '附件07', null=True, blank=True, help_text='附件07', upload_to='user/%Y/%m/%d/'
    )
    fujian_08 = models.FileField(
        '附件08', null=True, blank=True, help_text='附件08', upload_to='user/%Y/%m/%d/'
    )
    fujian_09 = models.FileField(
        '附件09', null=True, blank=True, help_text='附件09', upload_to='user/%Y/%m/%d/'
    )
    fujian_10 = models.FileField(
        '附件10', null=True, blank=True, help_text='附件10', upload_to='user/%Y/%m/%d/'
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = '02.用户'
        verbose_name_plural = verbose_name
        # permissions = (
        #     ("can_audit_task", "可审批任务"),
        #     ("can_audit_work", "可审批工作纪实"),
        # )
        ordering = ['department', 'sort_num', '-pk']

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    @property
    def first_name(self):
        return self.full_name

    @property
    def last_name(self):
        return self.full_name

    @property
    def category_names(self):
        return ",".join(self.category.all().values_list('name', flat=True))

    def email_user(self, subject, message, from_email=None, **kwargs):
        if self.email:
            send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.full_name

    def move_to(self, target, position):
        users = target.department.users.exclude(pk=self.pk).values_list('pk', flat=True).order_by('sort_num', '-pk')
        users = list(users)
        try:
            target_index = users.index(target.pk)
        except ValueError:
            return
        if position == 'left':
            users = users[:target_index] + [self.pk] + users[target_index:]
        elif position == 'right':
            users = users[:target_index+1] + [self.pk] + users[target_index+1:]
        else:
            return
        for index, uid in enumerate(users):
            User.objects.filter(pk=uid).update(sort_num=index)

    @property
    def func_names(self):
        group_permission_names = self.func_groups.all().values('permissions__name').distinct().values_list('permissions__name', flat=True)
        permission_names = self.func_user_permissions.all().values_list('name', flat=True)
        names = {*group_permission_names, *permission_names}
        return list(names)

    @property
    def func_codenames(self):
        group_permission_names = self.func_groups.all().values('permissions__codename').distinct().values_list('permissions__codename', flat=True)
        permission_names = self.func_user_permissions.all().values_list('codename', flat=True)
        names = {*group_permission_names, *permission_names}
        return list(names)

    @property
    def func_group_names(self):
        return list(self.func_groups.values_list('name', flat=True))


# 机构部门模型
class Department(MPTTModel):
    CATEGORYS = (
        ('', '未选择'),
        ('客服', '客服'),
        ('仓库', '仓库'),
        ('检验室', '检验室'),
    )
    name = models.CharField('名称', max_length=50, help_text='名称')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name='上级',
                            db_index=True, on_delete=models.CASCADE, help_text='上级')
    category = models.CharField('类别', max_length=15, choices=CATEGORYS, default='')
    contact_name = models.CharField('联系人', max_length=16, null=True, blank=True, help_text='联系人')
    contact_phone = models.CharField('联系电话', max_length=32, null=True, blank=True, help_text='联系电话')
    contact_mobile = models.CharField('手机号', max_length=32, null=True, blank=True, help_text='手机号')
    contact_fax = models.CharField('传真', max_length=32, null=True, blank=True, help_text='传真')
    description = models.TextField('说明', null=True, blank=True, help_text='说明')

    fdeptid = models.IntegerField('部门', null=True, blank=True, help_text='部门代码（FItemID）')
    fparentid = models.IntegerField('上级部门', null=True, blank=True, help_text='上级部门内码（FParentID）')

    open_time = models.TimeField('开门时间', default=datetime.time(9, 0, 0))
    close_time = models.TimeField('闭店时间', default=datetime.time(19, 0, 0))

    class Meta:
        verbose_name = '01.机构部门'
        verbose_name_plural = verbose_name

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_dep_path_name(self):
        names = self.get_ancestors(include_self=True).values_list('name', flat=True)
        return "/".join(names)


# 用户部门变更记录
class UserDepChange(models.Model):
    """用户部门变更记录"""
    user = models.ForeignKey('User', verbose_name='用户', on_delete=models.CASCADE,
                             help_text='用户', related_name='dep_changes')
    old_department = models.ForeignKey('Department', verbose_name='老部门', related_name='+',
                                       on_delete=models.CASCADE, help_text='老部门')
    new_department = models.ForeignKey('Department', verbose_name='新部门', related_name='+',
                                       on_delete=models.CASCADE, help_text='新部门')
    create_time = models.DateTimeField('更改时间', auto_now_add=True, blank=True)

    class Meta:
        verbose_name = '用户部门变更记录'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return "{0} {1} {2}->{3}".format(
            self.user.full_name, self.create_time, self.old_department, self.new_department
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        self.user.department = self.new_department
        self.user.save()


# 用户登录记录
class UserLoginLog(models.Model):
    """用户登录记录"""
    user = models.ForeignKey('User', on_delete=models.SET_NULL, default=None, null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    full_name = models.CharField(max_length=150, null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    ipaddress = models.CharField(max_length=128, null=True, blank=True)
    login_type = models.CharField(max_length=127, null=True, blank=True, default='PC')

    class Meta:
        verbose_name = '08.用户登录日志'
        verbose_name_plural = verbose_name
        ordering = ['-login_time']


# 手机验证码
class PhoneAccess(models.Model):
    phone = models.CharField('手机号码', max_length=30, primary_key=True, help_text='手机号码')
    phone_access = models.CharField('验证码', max_length=10, help_text='验证码')
    create_time = models.DateTimeField('发送时间', auto_now=True, help_text='发送时间')

    class Meta:
        verbose_name = '05.手机验证码'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']


# 用户注册申请
class UserRequire(models.Model):
    STATES = (
        ('未审核', '未审核'),
        ('未通过', '未通过'),
        ('已同意', '已同意'),
    )
    phone = models.CharField('手机号', max_length=20, help_text='手机号')
    phone_access = models.CharField('验证码', max_length=10, help_text='验证码', null=True, blank=True)
    full_name = models.CharField('姓名', max_length=31, help_text='姓名')
    group = models.ForeignKey(
        'usercenter.FuncGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_request',
        help_text='身份',
        db_constraint=False
    )
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_request',
        help_text='部门',
        db_constraint=False
    )
    audit_user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='审批用户',
        db_constraint=False
    )
    audit_time = models.DateTimeField('审批时间', null=True, blank=True, help_text='审批时间')
    state = models.CharField('审核状态', max_length=5, choices=STATES, default='未审核', help_text='审核状态')
    create_time = models.DateTimeField('创建时间', auto_now_add=True, help_text='创建时间')
    denial_reason = models.TextField('拒绝员因', null=True, blank=True, help_text='拒绝员因')
    remark = models.TextField('备注', null=True, blank=True, help_text='备注')
    target_user = models.OneToOneField(
        'User', null=True, blank=True, help_text='对应用户', on_delete=models.SET_NULL, db_constraint=False,
        related_name='joinrequest'
    )
    password = models.CharField('密码', max_length=127, null=True, blank=True, help_text='密码')

    category = models.ManyToManyField(
        'baseconfig.BaseConfigItem', blank=True, verbose_name='分类', help_text='分类', related_name='user_requires'
    )

    field_01 = models.TextField('附加内容01', null=True, blank=True, help_text='附加内容01')
    field_02 = models.TextField('附加内容02', null=True, blank=True, help_text='附加内容02')
    field_03 = models.TextField('附加内容03', null=True, blank=True, help_text='附加内容03')
    field_04 = models.TextField('附加内容04', null=True, blank=True, help_text='附加内容04')
    field_05 = models.TextField('附加内容05', null=True, blank=True, help_text='附加内容05')

    fujian_01 = models.FileField(
        '附件01', null=True, blank=True, help_text='附件01', upload_to='userrequire/%Y/%m/%d/'
    )
    fujian_02 = models.FileField(
        '附件02', null=True, blank=True, help_text='附件02', upload_to='userrequire/%Y/%m/%d/'
    )
    fujian_03 = models.FileField(
        '附件03', null=True, blank=True, help_text='附件03', upload_to='userrequire/%Y/%m/%d/'
    )
    fujian_04 = models.FileField(
        '附件04', null=True, blank=True, help_text='附件04', upload_to='userrequire/%Y/%m/%d/'
    )
    fujian_05 = models.FileField(
        '附件05', null=True, blank=True, help_text='附件05', upload_to='userrequire/%Y/%m/%d/'
    )
    fujian_06 = models.FileField(
        '附件06', null=True, blank=True, help_text='附件06', upload_to='userrequire/%Y/%m/%d/'
    )
    fujian_07 = models.FileField(
        '附件07', null=True, blank=True, help_text='附件07', upload_to='userrequire/%Y/%m/%d/'
    )
    fujian_08 = models.FileField(
        '附件08', null=True, blank=True, help_text='附件08', upload_to='userrequire/%Y/%m/%d/'
    )
    fujian_09 = models.FileField(
        '附件09', null=True, blank=True, help_text='附件09', upload_to='userrequire/%Y/%m/%d/'
    )
    fujian_10 = models.FileField(
        '附件10', null=True, blank=True, help_text='附件10', upload_to='userrequire/%Y/%m/%d/'
    )

    class Meta:
        verbose_name = '06.用户加入申请'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def create_user(self):
        if User.objects.filter(username=self.phone):
            raise ValueError('该手机号码已存在！')
        user = User.objects.create_user(
            self.phone, uuid.uuid4().hex,
            full_name=self.full_name,
            mobile=self.phone,
            field_01=self.field_01,
            field_02=self.field_02,
            field_03=self.field_03,
            field_04=self.field_04,
            field_05=self.field_05,
        )
        for i in self.category.all():
            user.category.add(i)
        group, created = FuncGroup.objects.get_or_create(name='供应商')
        user.func_groups.add(group)
        self.target_user = user
        self.save()
        if self.password and len(self.password) >= 6:
            user.set_password(self.password)
            user.save()
        return user

    @property
    def category_names(self):
        return ",".join(self.category.all().values_list('name', flat=True))

    @property
    def group_display(self):
        return self.group.name

    @property
    def department_display(self):
        return self.department.name

    @property
    def create_time_display(self):
        return self.create_time.strftime('%Y-%m-%d %H:%M')


# 用户离职申请
class LeaveRequire(models.Model):
    STATES = (
        ('未审核', '未审核'),
        ('未通过', '未通过'),
        ('已同意', '已同意'),
    )
    user = models.ForeignKey('User', on_delete=models.CASCADE, help_text='用户', db_constraint=False)
    leave_reason = models.TextField('离职原因', null=True, blank=True, help_text='离职原因')
    leave_date = models.DateField('离职日期', help_text='离职日期')
    denial_reason = models.TextField('拒绝员因', null=True, blank=True, help_text='拒绝员因')
    state = models.CharField('审核状态', max_length=5, choices=STATES, default='未审核', help_text='审核状态')
    audit_user = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True,
        help_text='审批用户', related_name='leaverequire_audit', db_constraint=False
    )
    audit_time = models.DateTimeField('审批时间', null=True, blank=True, help_text='审批时间')
    create_time = models.DateTimeField('申请时间', auto_now_add=True, help_text='申请时间')

    class Meta:
        verbose_name = '07.离职申请'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
