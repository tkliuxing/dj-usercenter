from django import forms
from mptt.forms import TreeNodeChoiceField
from . import models


class UserForm(forms.ModelForm):
    department = TreeNodeChoiceField(queryset=models.Department.objects.all())
    password = forms.CharField(required=False, label='密码', widget=forms.PasswordInput)

    class Meta:
        model = models.User
        fields = ['username', 'full_name', 'email', 'phone', 'mobile', 'inner_code', 'employee_position',
                  'employee_rank', 'sex', 'marital_status', 'home_address', 'birthplace', 'birthday',
                  'nationality', 'political_status', 'educational_level', 'sort_num',
                  'description', 'department', 'is_active', 'password', 'groups']


class UserListForm(forms.ModelForm):
    password = forms.CharField(required=True, label='密码', widget=forms.PasswordInput)
    class Meta:
        model = models.User
        fields = ['username', 'full_name', 'email', 'phone', 'mobile', 'inner_code', 'employee_position',
                  'employee_rank', 'sex', 'marital_status', 'home_address', 'birthplace', 'birthday',
                  'nationality', 'political_status', 'educational_level', 'sort_num',
                  'description', 'department', 'is_active', 'password', 'groups']


class MyInfoForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['full_name', 'email', 'phone', 'mobile', 'employee_position',
                  'employee_rank', 'sex', 'marital_status', 'home_address', 'birthplace', 'birthday',
                  'nationality', 'political_status', 'educational_level',
                  'description']


class DepartmentMoveForm(forms.Form):
    POSITION_CHOICES = (
        ('first-child', '第一个子部门'),
        ('last-child', '最后一个子部门'),
        ('left', '之前'),
        ('right', '之后'),
    )
    department = forms.ModelChoiceField(queryset=models.Department.objects.all(), widget=forms.HiddenInput)
    departments = TreeNodeChoiceField(queryset=models.Department.objects.all(), label='部门')
    position = forms.ChoiceField(label='位置', choices=POSITION_CHOICES)


class UserOrderForm(forms.Form):
    USER_POSITION_CHOICES = (
        ('left', '之前'),
        ('right', '之后'),
    )
    user = forms.IntegerField(
        label='当前用户',
        help_text='当前用户',
        widget=forms.HiddenInput
    )
    target = forms.ModelChoiceField(
        label='目标用户',
        help_text='目标用户',
        queryset=models.User.objects.none()
    )
    position = forms.ChoiceField(
        label='位置',
        help_text='位置',
        choices=USER_POSITION_CHOICES
    )

    def __init__(self, users=None, *args, **kwargs):
        super(UserOrderForm, self).__init__(*args, **kwargs)
        if users:
            self.fields['target'].queryset = users

    def save(self):
        validated_data = self.cleaned_data
        user = models.User.objects.get(pk=validated_data['user'])
        target = validated_data['target']
        user.move_to(target, validated_data['position'])
        return user
