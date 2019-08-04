from django.urls import path, include
from rest_framework import routers

from . import api

router = routers.DefaultRouter()
router.register(r'user', api.UserViewSet)
router.register(r'department', api.DepartmentViewSet)
router.register(r'changepwd', api.ChangePasswordApi)

urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)
