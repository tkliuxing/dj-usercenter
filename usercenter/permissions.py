from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class IsMPCustomerOrIsAuthenticated(permissions.IsAuthenticated):
    """微信用户以及登录用户"""
    def has_permission(self, request, view):
        from customer.models import Customer
        mp_openid = request.headers.get('Openid')
        if mp_openid:
            customers = Customer.objects.filter(wechart_oid=mp_openid)
            if customers:
                return True
        return bool(request.user and request.user.is_authenticated)
