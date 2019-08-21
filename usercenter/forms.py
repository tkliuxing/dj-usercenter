from django import forms
from mptt.forms import TreeNodeChoiceField
from . import models


class UserForm(forms.ModelForm):
    department = TreeNodeChoiceField(queryset=models.Department.objects.all())

    class Meta:
        model = models.User
        fields = ['username', 'full_name', 'email', 'phone', 'mobile', 'inner_code', 'employee_position',
                  'employee_rank', 'sex', 'marital_status', 'home_address', 'birthplace', 'birthday',
                  'nationality', 'political_status', 'educational_level', 'sort_num',
                  'description', 'department', 'is_active']


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
