from django.urls import path, include
from django.conf.urls import url
from django.views.generic import TemplateView
from rest_framework import routers

from . import api
from . import views

router = routers.DefaultRouter()
router.register(r'user', api.UserViewSet)
router.register(r'userorder', api.UserOrderView)
router.register(r'group', api.GroupViewSet)
router.register(r'department', api.TreeDepartmentViewSet)
router.register(r'flatdepartment', api.DepartmentViewSet)
router.register(r'departmentmove', api.DepartmentMoveView)
router.register(r'userdepchange', api.UserDepChangeViewSet)
router.register(r'changepwd', api.ChangePasswordApi)
router.register(r'myinfo', api.MyInfoViewSet)

urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
    url(r'myinfo/0/$', views.MyInfoUpdateView.as_view(), name='myinfo'),
    url(r'myinfo/success/$', views.MyInfoUpdateSuccessView.as_view(), name='myinfo_success'),
    url(r'user/$', views.UserListView.as_view(), name='userlist'),
    url(r'user/add/', views.UserCreateView.as_view(), name='user_add'),
    url(r'user/detail/(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user_detail'),
    url(r'user/update/(?P<pk>\d+)/', views.UserUpdateView.as_view(), name='user_update'),
    url(r'user/delete/(?P<pk>\d+)/', views.UserDeleteView.as_view(), name='user_delete'),
    url(r'user/order/(?P<pk>\d+)/', views.UserOrderView.as_view(), name='user_order'),
    url(r'user/dep/(?P<pk>\d+)/', views.UserDepChangeView.as_view(), name='user_dep'),  # 部门变更
    url(r'user/group/$', views.GroupListView.as_view(), name='user_group'),  # 角色管理
    url(r'user/passwdchange/$', views.PasswordChangeView.as_view(), name='passwdchange'),
    url(r'user/passwdchange/success/$', views.PasswordChangeSuccessView.as_view(), name='changepwdsuccess'),
    url(r'department/$', views.DepartmentListView.as_view(), name='department_list'),  # 组织机构列表
    url(r'department/add/$', views.DepartmentCreateView.as_view(), name='department_add'),  # 组织机构新增
    url(r'department/update/(?P<pk>\d+)/$', views.DepartmentUpdateView.as_view(), name='department_update'),  # 组织机构新增
    url(r'department/detail/(?P<pk>\d+)/$', views.DepartmentDetailView.as_view(), name='department_detail'),  # 组织机构详细
    url(r'department/delete/(?P<pk>\d+)/$', views.DepartmentDeleteView.as_view(), name='department_delete'),  # 组织机构删除
    url(r'department/movie/$', views.DepartmentMoveView.as_view(), name='department_movie'),  # 组织机构移动
    url(r'department/tips/$', TemplateView.as_view(template_name='usercenter/department_tips.html'),
        name='department_tips'),  # 操作完成
)
