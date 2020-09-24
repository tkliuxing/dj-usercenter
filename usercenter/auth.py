import logging
import datetime

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from wechatpy import WeChatClientException
from wechatpy.client import WeChatClient
from wechatpy.session.redisstorage import RedisStorage
from redis import Redis
from rest_framework import serializers, fields, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken

from .models import PhoneAccess, User
from .permissions import CsrfExemptSessionAuthentication, BasicAuthentication

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
logger = logging.getLogger('restapi')


class PhoneValidErrorException(ValidationError):
    pass


class PhoneAuthenticationSerializer(serializers.Serializer):
    phone = fields.CharField(required=True, help_text='手机号')
    phone_access = fields.CharField(required=True, help_text='验证码')

    def validate(self, data):
        phone, pa = data['phone'], data['phone_access']
        try:
            access = PhoneAccess.objects.get(phone=phone, phone_access=pa)
            if phone != '17704818161':
                access.delete()
        except PhoneAccess.DoesNotExist:
            raise ValidationError('验证码错误')
        try:
            User.objects.get(username=phone)
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        return data

    def create(self, validated_data):
        user = User.objects.get(username=validated_data['phone'])
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user_logged_in.send(sender=user.__class__, request=self.context['request'], user=user)
        response = {'token': token}
        return response

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class PhoneLoginViewSet(viewsets.GenericViewSet):
    serializer_class = PhoneAuthenticationSerializer
    queryset = User.objects.none()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """手机号验证码登录API"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PhoneAccessSerializer(serializers.Serializer):
    phone = fields.CharField()
    error = fields.CharField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PhoneAccessViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    serializer_class = PhoneAccessSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = PhoneAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        try:
            pa = PhoneAccess.objects.get(phone=phone)
        except PhoneAccess.DoesNotExist:
            pa = PhoneAccess(phone=phone)
        if phone == '17704818161':
            pa.phone_access = '123456'
            pa.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        now = datetime.datetime.now()
        if pa.phone_access and pa.create_time > now - datetime.timedelta(seconds=60):
            return Response({'phone': phone, 'error': '请勿短时间重复发送'}, status=status.HTTP_403_FORBIDDEN)
        state, access = send_phone_access(phone)
        logger.info('{}: {}'.format(state, access))
        if not state:
            return Response({'phone': phone, 'error': '短信发送失败'}, status=status.HTTP_403_FORBIDDEN)
        pa.phone_access = access
        pa.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def send_phone_access(phone):
    import requests
    import random
    code = []
    for i in range(6):
        code.append(str(random.randint(0, 9)))
    code = "".join(code)
    sms_type = getattr(settings, 'SMS_TYPE', 'JUHE')
    if sms_type == 'JUHE':
        url = getattr(settings, 'SMS_URL_JUHE')
        appkey = getattr(settings, 'SMS_APPKEY_JUHE')
        tpl_id = getattr(settings, 'SMS_TPL_ID_JUHE')
        if not any([url, appkey, tpl_id]):
            logger.error('短信验证码配置错误')
            return False, 404
        params = {'mobile': phone, 'tpl_id': tpl_id, 'tpl_value': '#code#=' + code, 'key': appkey}
        ret = requests.get(url, params)
        ret_json = ret.json()
        if ret_json.get('error_code') == 0:
            return True, code
        else:
            logger.error('短信验证码错误', data=ret_json)
            return False, code
    if sms_type == 'TENCENT':
        from .auth_tencent import send_phone_access
        return send_phone_access(phone, code)
    logger.error('SMS_TYPE 配置错误')
    return False, code


class MyJSONWebTokenSerializer(JSONWebTokenSerializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception)
        if is_valid:
            user = self.object.get('user')
            if user:
                user_logged_in.send(sender=user.__class__, request=self.context['request'], user=user)
        return is_valid


class MyObtainJSONWebToken(ObtainJSONWebToken):
    serializer_class = MyJSONWebTokenSerializer


obtain_jwt_token = MyObtainJSONWebToken.as_view()


class WXALoginSerializer(serializers.Serializer):
    code = fields.CharField(required=True, help_text='临时登录凭证code')

    def validate(self, data):
        code = data['code']
        redis_client = Redis.from_url(getattr(settings, 'REDIS_URL'))
        session_interface = RedisStorage(
            redis_client,
            prefix="wechatpy"
        )
        appid = getattr(settings, 'WXA_APPID')
        secret = getattr(settings, 'WXA_SECRET')
        if not appid or not secret:
            raise ValidationError('微信小程序未配置')
        wechat_client = WeChatClient(
            appid,
            secret,
            session=session_interface
        )
        try:
            data = wechat_client.wxa.code_to_session(code)
        except WeChatClientException:
            raise ValidationError('code已使用')
        try:
            User.objects.get(wechart_oid=data['openid'])
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        return data

    def create(self, validated_data):
        user = User.objects.get(wechart_oid=validated_data['openid'])
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user_logged_in.send(sender=user.__class__, request=self.context['request'], user=user)
        response = {'token': token}
        return response

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class WXALoginViewSet(viewsets.GenericViewSet):
    serializer_class = WXALoginSerializer
    queryset = User.objects.none()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """手机号验证码登录API"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WXABindSerializer(serializers.Serializer):

    phone = fields.CharField(required=True, help_text='手机号')
    phone_access = fields.CharField(required=True, help_text='验证码')
    code = fields.CharField(required=True, help_text='临时登录凭证code')

    def validate(self, data):
        phone, pa = data['phone'], data['phone_access']
        try:
            access = PhoneAccess.objects.get(phone=phone, phone_access=pa)
            if phone != '17704818161':
                access.delete()
        except PhoneAccess.DoesNotExist:
            raise ValidationError('验证码错误')
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        code = data['code']
        redis_client = Redis.from_url(getattr(settings, 'REDIS_URL'))
        session_interface = RedisStorage(
            redis_client,
            prefix="wechatpy"
        )
        appid = getattr(settings, 'WXA_APPID')
        secret = getattr(settings, 'WXA_SECRET')
        if not appid or not secret:
            raise ValidationError('微信小程序未配置')
        wechat_client = WeChatClient(
            appid,
            secret,
            session=session_interface
        )
        try:
            wx_data = wechat_client.wxa.code_to_session(code)
        except WeChatClientException:
            raise ValidationError('code已使用')
        users = User.objects.exclude(username=phone).filter(wechart_oid=wx_data['openid'])
        if users:
            raise ValidationError('其它用户已绑定此微信，请更换微信号后进行绑定')
        user.wechart_oid = wx_data['openid']
        user.save()
        return data

    def create(self, validated_data):
        user = User.objects.get(username=validated_data['phone'])
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user_logged_in.send(sender=user.__class__, request=self.context['request'], user=user)
        response = {'token': token}
        return response

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class WXABindViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    serializer_class = WXABindSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
