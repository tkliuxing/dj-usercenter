from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView, TemplateView
from django.views.generic import FormView
from django_filters.views import FilterView
from django.contrib.auth.models import Group

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
    form_class = forms.UserForm
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


class UserDepChangeView(LoginRequiredMixin, CreateView):
    model = models.UserDepChange
    # 要获取显示的数据信息
    fields = ['user', 'old_department', 'new_department']
    template_name = 'usercenter/user_dep_change.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['user_data'] = models.User.objects.get(pk=self.kwargs['pk'])
        return context_data

    def get_success_url(self):
        return reverse('userlist') + '?department=' + str(self.object.new_department.pk)


# 用户修改信息视图
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = models.User
    form_class = forms.UserForm

    # 保存数据
    def form_valid(self, form):
        passwd = self.get_object().password
        user = form.save()
        password = self.request.POST.get('password')
        # 判断密码是否存在
        if password:
            user.set_password(password)
            user.save()
        else:
            user.password = passwd
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


# 组织机构信息
class GroupListView(LoginRequiredMixin, ListView):
    queryset = Group.objects.all()
    context_object_name = 'group'
    template_name = 'usercenter/user_group.html'


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


class PasswordChangeView(LoginRequiredMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'usercenter/password_change.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        from django.contrib.auth import authenticate
        from django.contrib.auth.views import auth_login
        user = form.save()
        user = authenticate(self.request, username=user.username, password=form.cleaned_data['new_password1'])
        auth_login(self.request, user)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('changepwdsuccess')


class PasswordChangeSuccessView(TemplateView):
    template_name = 'usercenter/password_change_success.html'


class UserOrderView(LoginRequiredMixin, FormView):
    form_class = forms.UserOrderForm
    template_name = 'usercenter/user_order.html'

    def get_form(self, form_class=None):
        user = self.get_user()
        form = forms.UserOrderForm(
            users=user.department.users.exclude(pk=user.pk),
            **self.get_form_kwargs()
        )
        return form

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['user'] = self.get_user()
        return context_data

    def get_initial(self):
        return {'user': self.get_user().pk}

    def form_valid(self, form):
        result = super().form_valid(form)
        form.save()
        return result

    def get_user(self):
        return models.User.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        user = self.get_user()
        return reverse('userlist') + '?department=' + str(user.department.pk)


class MyInfoUpdateView(LoginRequiredMixin, UpdateView):
    form_class = forms.MyInfoForm
    template_name = 'usercenter/myinfo.html'
    success_url = reverse_lazy('myinfo_success')

    def get_object(self, queryset=None):
        return self.request.user


class MyInfoUpdateSuccessView(TemplateView):
    template_name = 'usercenter/password_change_success.html'
