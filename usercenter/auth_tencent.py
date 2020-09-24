
import logging
from django.conf import settings
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20190711 import sms_client
from tencentcloud.sms.v20190711 import models as sms_models

logger = logging.getLogger('restapi')

def send_phone_access(phone, code):
    secret_id = getattr(settings, 'TENCENT_CLOUD_SECRETID')
    secret_key = getattr(settings, 'TENCENT_CLOUD_SECRETKEY')
    sms_appid = getattr(settings, 'SMS_APPID_TENCENT')
    sms_tplid = getattr(settings, 'SMS_TPL_ID_TENCENT')
    sms_tpl_sign = getattr(settings, 'SMS_TPL_SIGN_TENCENT')
    if not secret_id or not secret_key:
        logger.error('TENCENT CLOUD 配置错误')
        return False, 404
    if not sms_appid or not sms_tplid or not sms_tpl_sign:
        logger.error('TENCENT SMS 配置错误')
        return False, 404
    try:
        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = "sms.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = sms_client.SmsClient(cred, "", client_profile)
        req = sms_models.SendSmsRequest()
        req.SmsSdkAppid = sms_appid
        req.Sign = sms_tpl_sign
        req.ExtendCode = ""
        req.SenderId = ""
        req.PhoneNumberSet = ["+86" + phone]
        req.TemplateID = sms_tplid
        req.TemplateParamSet = [code]
        resp = client.SendSms(req)
        if resp.SendStatusSet[0].Code != 'Ok':
            logger.error(resp.to_json_string())
            return False, 404
        return True, code
    except TencentCloudSDKException as e:
        logger.error(e)
