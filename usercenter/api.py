from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response

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
    """ViewSet for the Task class"""

    queryset = models.User.objects.exclude(username='AnonymousUser')
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['full_name', 'department']
    search_fields = ['full_name']

    def perform_create(self, serializer):
        instance = serializer.save()
        if self.request.data.get('password'):
            instance.set_password(self.request.data.get('password'))
            instance.save()


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for the Work class"""

    queryset = models.Department.objects.all()
    serializer_class = serializers.FlatDepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class TreeDepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for the Work class"""

    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(models.Department.objects.root_nodes(), many=True)
        return Response(serializer.data)


class MyInfoViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.User.objects.none()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)
