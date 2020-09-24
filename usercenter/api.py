from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from usercenter.models import FuncGroup
from .filters import UserFilterSet
from .permissions import CsrfExemptSessionAuthentication, BasicAuthentication
from . import models
from . import serializers


class ChangePasswordApi(viewsets.GenericViewSet):
    """
    修改密码

    create:
    修改用户密码.
    """
    queryset = models.User.objects.none()
    serializer_class = serializers.ChangePwdSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'error': False, 'msg': '修改成功'})
        else:
            return Response({'error': True, 'msg': '原密码不正确'})


class UserViewSet(viewsets.ModelViewSet):
    """用户API"""

    queryset = models.User.objects.exclude(username='AnonymousUser', is_active=False)
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilterSet
    search_fields = ['full_name', 'mobile']

    def perform_create(self, serializer):
        super().perform_create(serializer)
        if self.request.data.get('password'):
            serializer.instance.set_password(self.request.data.get('password'))
            serializer.instance.save()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        if self.request.data.get('password'):
            serializer.instance.set_password(self.request.data.get('password'))
            serializer.instance.save()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """权限API"""
    queryset = models.FuncPermission.objects.all()
    serializer_class = serializers.FuncPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None


class GroupViewSet(viewsets.ModelViewSet):
    """权限组API"""
    queryset = models.FuncGroup.objects.order_by('pk')
    serializer_class = serializers.FuncGroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class DepartmentViewSet(viewsets.ModelViewSet):
    """机构部门API"""

    queryset = models.Department.objects.all()
    serializer_class = serializers.FlatDepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_fields = ('category',)
    search_fields = ('name', )


class TreeDepartmentViewSet(viewsets.ModelViewSet):
    """树形机构部门API"""

    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(models.Department.objects.root_nodes(), many=True)
        return Response(serializer.data)


class MyInfoViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    """我的信息API"""
    queryset = models.User.objects.none()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)


class UserDepChangeViewSet(viewsets.ModelViewSet):
    """用户部门变更"""
    queryset = models.UserDepChange.objects.all()
    serializer_class = serializers.UserDepChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'old_department', 'new_department']
    search_fields = ['user__full_name']


class DepartmentMoveView(viewsets.GenericViewSet):
    """部门排列移动"""
    queryset = models.Department.objects.none()
    serializer_class = serializers.DepartmentMoveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'error': False, 'msg': '修改成功'})
        else:
            return Response({'error': True, 'msg': serializer.errors})


class UserOrderView(viewsets.GenericViewSet):
    """用户排序API"""
    queryset = models.User.objects.none()
    serializer_class = serializers.UserOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'error': False, 'msg': '修改成功'})
        else:
            return Response({'error': True, 'msg': serializer.errors})


class UserLoginLogViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    """用户登录日志API"""
    queryset = models.UserLoginLog.objects.all()
    serializer_class = serializers.UserLoginLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user',)


class UserRequireViewSet(viewsets.ModelViewSet):
    """用户申请API"""
    queryset = models.UserRequire.objects.order_by('-create_time')
    serializer_class = serializers.UserRequireSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['state', 'department']
    search_fields = ['full_name', 'phone']


class UserRequireCreateView(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    """用户申请创建API"""
    queryset = models.UserRequire.objects.none()
    serializer_class = serializers.UserRequireCreateSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny, )


class UserRequireDepartmentListView(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    """用户申请门店信息API"""
    queryset = models.Department.objects.root_nodes()
    serializer_class = serializers.DepartmentMiniSerializer
    permission_classes = (AllowAny, )


class UserRequireGroupListView(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    """用户申请身份信息API"""
    queryset = FuncGroup.objects.all()
    serializer_class = serializers.FuncGroupMiniSerializer
    permission_classes = (AllowAny, )


class UserRequirePassView(viewsets.mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """用户申请通过API"""
    queryset = models.UserRequire.objects.all()
    serializer_class = serializers.UserRequirePassSerializer
    permission_classes = [permissions.IsAuthenticated]


class LeaveRequireViewSet(viewsets.ModelViewSet):
    """离职申请API"""
    queryset = models.LeaveRequire.objects.all()
    serializer_class = serializers.LeaveRequireSerializer
    permission_classes = [permissions.IsAuthenticated]


class LeaveRequirePassView(viewsets.mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """离职申请通过API"""
    queryset = models.LeaveRequire.objects.all()
    serializer_class = serializers.LeaveRequirePassSerializer
    permission_classes = [permissions.IsAuthenticated]
