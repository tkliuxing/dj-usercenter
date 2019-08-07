from django.urls import path, include
from rest_framework import routers

from . import api

router = routers.DefaultRouter()
router.register(r'user', api.UserViewSet)
router.register(r'group', api.GroupViewSet)
router.register(r'department', api.TreeDepartmentViewSet)
router.register(r'flatdepartment', api.DepartmentViewSet)
router.register(r'changepwd', api.ChangePasswordApi)
router.register(r'myinfo', api.MyInfoViewSet)

urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)
