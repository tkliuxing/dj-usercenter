from rest_framework import viewsets, permissions
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


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for the Work class"""

    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(models.Department.objects.root_nodes(), many=True)
        return Response(serializer.data)
