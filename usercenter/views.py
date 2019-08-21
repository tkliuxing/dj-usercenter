from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.views.generic import FormView
from django_filters.views import FilterView

from . import forms
from . import models


# 获取某部门下用户列表
class UserListView(LoginRequiredMixin, FilterView):
    model = models.User
    filterset_fields = ['department']
    context_object_name = 'users'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)
        dep_id = self.request.GET.get('department', 0)
        data['department'] = dep_id
        if dep_id:
            data['dep'] = get_object_or_404(models.Department, pk=dep_id)
        return data


# 用户详细信息
class UserDetailView(LoginRequiredMixin, DetailView):
    model = models.User
    context_object_name = 'user'


# 创建用户信息
class UserCreateView(LoginRequiredMixin, CreateView):
    model = models.User
    # 要获取显示的数据信息
    fields = ['username', 'full_name', 'email', 'phone', 'mobile', 'inner_code', 'employee_position',
              'employee_rank', 'sex', 'marital_status', 'home_address', 'birthplace', 'birthday',
              'nationality', 'political_status', 'educational_level', 'sort_num',
              'description', 'department', 'is_active']
    template_name = 'usercenter/user_add.html'

    def get_initial(self):
        dep_id = self.request.GET.get('department')
        if dep_id:
            dep = get_object_or_404(models.Department, pk=dep_id)
            return {
                'department': dep
            }
        else:
            return {}

    def form_valid(self, form):
        password = form.cleaned_data['password']
        user = form.save()
        user.set_password(password)
        user.save()
        self.object = user
        return HttpResponseRedirect(reverse('userlist') + "?department=" + str(user.department_id))


# 用户修改信息视图
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = models.User
    form_class = forms.UserForm

    # 保存数据
    def form_valid(self, form):
        user = form.save()
        password = self.request.POST.get('password')
        # 判断密码是否存在
        if password:
            user.set_password(password)
            user.save()
        self.object = user
        return HttpResponseRedirect(reverse('userlist') + "?department=" + str(user.department_id))


# 用户删除信息
class UserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.User
    # 获取在usercenter这个APP的删除权限
    permission_required = ['usercenter.delete_user']

    def get_success_url(self):
        return reverse('userlist') + "?department=" + str(self.object.department_id)


# 创建组织机构信息
class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = models.Department
    # 要获取显示的数据信息
    fields = ['name', 'parent', 'contact_name', 'contact_phone', 'contact_mobile', 'contact_fax', 'description']
    template_name = 'usercenter/department_add.html'

    def get_initial(self):
        dep_id = self.request.GET.get('department')
        print(dep_id)
        if dep_id:
            dep = get_object_or_404(models.Department, pk=dep_id)
            return {
                'parent': dep
            }
        else:
            return {}

    def form_valid(self, form):
        department = form.save()
        self.object = department
        return redirect('department_tips')
        # return redirect('department_detail', pk=department.pk)


# 组织机构信息
class DepartmentListView(LoginRequiredMixin, ListView):
    model = models.Department
    context_object_name = 'department'


# 组织机构修改信息视图
class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Department
    # 要获取显示的数据信息
    fields = ['name', 'parent', 'contact_name', 'contact_phone', 'contact_mobile', 'contact_fax', 'description']

    # 保存数据
    def form_valid(self, form):
        department = form.save()

        self.object = department
        return redirect('department_detail', pk=department.pk)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['move_form'] = forms.DepartmentMoveForm(initial={'department': self.object})
        return data


# 组织机构详细信息
class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = models.Department
    context_object_name = 'department'


class DepartmentMoveView(LoginRequiredMixin, FormView):
    form_class = forms.DepartmentMoveForm
    template_name = 'usercenter/department_move_form.html'

    def get_success_url(self):
        return reverse('department_tips')

    def form_valid(self, form):
        department = form.cleaned_data['department']
        to_dep = form.cleaned_data['departments']
        position = form.cleaned_data['position']
        if department != to_dep:
            department.move_to(to_dep, position)
        return super().form_valid(form)


# 组织机构删除信息
class DepartmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Department
    # 获取在usercenter这个APP的删除权限
    permission_required = ['usercenter.delete_department']

    def get_success_url(self):
        return reverse('department_tips')
