from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from . import models

@receiver(user_logged_in)
def add_user_login_log(sender, request, user, **kwargs):
    models.UserLoginLog.objects.create(
        user=user, username=user.username, full_name=user.full_name,
        ipaddress=request.META.get('REMOTE_ADDR')
    )
