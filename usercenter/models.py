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
    EMPLOYEE_RANKS = (
        ('领导班子', '领导班子'),
        ('中层干部', '中层干部'),
        ('普通', '普通'),
    )
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
    employee_rank = models.CharField('职别', max_length=32, choices=EMPLOYEE_RANKS, null=True, blank=True)
    sex = models.CharField('性别', max_length=2, choices=(('男', '男'), ('女', '女'),), null=True, blank=True, help_text='性别')
    marital_status = models.CharField('婚姻状况', help_text='婚姻状况', null=True, blank=True,
                                      max_length=5, choices=(('已婚', '已婚'), ('未婚', '未婚'),))
    home_address = models.CharField('家庭住址', help_text='家庭住址', max_length=200, null=True, blank=True)
    birthplace = models.CharField('籍贯', help_text='籍贯', max_length=100, null=True, blank=True)
    birthday = models.DateField('出生年月日', help_text='出生年月日', null=True, blank=True)
    nationality = models.CharField('民族', help_text='民族', max_length=20, null=True, blank=True)
    political_status = models.CharField('政治面貌', help_text='政治面貌', max_length=50, blank=True, null=True)
    educational_level = models.CharField('文化程度', help_text='文化程度', max_length=20, blank=True, null=True)
    description = models.TextField('备注', null=True, blank=True, help_text='备注')
    department = models.ForeignKey('Department', null=True, blank=True, related_name='users',
                                   on_delete=models.SET_NULL, verbose_name='部门', help_text='部门')

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        # permissions = (
        #     ("can_audit_task", "可审批任务"),
        #     ("can_audit_work", "可审批工作纪实"),
        # )
        ordering = ['pk']

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

    def email_user(self, subject, message, from_email=None, **kwargs):
        if self.email:
            send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.username


# 机构部门模型
class Department(MPTTModel):
    CATEGORYS = (
        ('厅', '厅'),
        ('厅机关', '厅机关'),
        ('事业单位', '事业单位'),
    )
    name = models.CharField('名称', max_length=50, help_text='部门名称')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name='上级部门',
                            db_index=True, on_delete=models.CASCADE, help_text='上级部门')
    category = models.CharField('部门类别', max_length=15, choices=CATEGORYS, default='厅机关')
    contact_name = models.CharField('联系人', max_length=16, null=True, blank=True, help_text='联系人')
    contact_phone = models.CharField('联系电话', max_length=32, null=True, blank=True, help_text='联系电话')
    contact_mobile = models.CharField('手机号', max_length=32, null=True, blank=True, help_text='手机号')
    contact_fax = models.CharField('传真', max_length=32, null=True, blank=True, help_text='传真')
    description = models.TextField('说明', null=True, blank=True, help_text='说明')

    class Meta:
        verbose_name = '机构部门'
        verbose_name_plural = verbose_name

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_dep_path_name(self):
        names = self.get_ancestors(include_self=True).values_list('name', flat=True)
        return "/".join(names)


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
