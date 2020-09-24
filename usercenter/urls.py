from django.urls import path, include
from rest_framework import routers

from . import api
from . import auth
from . import views

router = routers.DefaultRouter()
router.register(r'user', api.UserViewSet)
router.register(r'userorder', api.UserOrderView)
router.register(r'group', api.GroupViewSet)
router.register(r'permissions', api.PermissionViewSet)
router.register(r'department', api.TreeDepartmentViewSet)
router.register(r'flatdepartment', api.DepartmentViewSet)
router.register(r'departmentmove', api.DepartmentMoveView)
router.register(r'userdepchange', api.UserDepChangeViewSet)
router.register(r'changepwd', api.ChangePasswordApi)
router.register(r'myinfo', api.MyInfoViewSet)
router.register(r'userloginlog', api.UserLoginLogViewSet)
router.register(r'userrequire', api.UserRequireViewSet)
router.register(r'userrequirecreate', api.UserRequireCreateView)
# router.register(r'userrequiredepartmentlist', api.UserRequireDepartmentListView)
# router.register(r'userrequiregrouplist', api.UserRequireGroupListView)
router.register(r'userrequirepass', api.UserRequirePassView)
# router.register(r'leaverequire', api.LeaveRequireViewSet)
# router.register(r'leaverequirepass', api.LeaveRequirePassView)

router.register(r'phoneauth', auth.PhoneAccessViewSet)
router.register(r'phonelogin', auth.PhoneLoginViewSet)
router.register(r'wxalogin', auth.WXALoginViewSet)
router.register(r'wxabind', auth.WXABindViewSet)

urlpatterns = (
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', auth.obtain_jwt_token),
)
