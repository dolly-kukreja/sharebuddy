import logging
from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet
from django.utils import timezone

from core.constants import OTPKeyNameTypes
from core.helpers.base import random_string_generator
from core.helpers.decorators import handle_unknown_exception
from core.models import OneTimePassword
from core.services.email import send_email
from core.services.sms import send_sms

LOGGER = logging.getLogger(__name__)


class OneTimePasswordRepository:
    def __init__(
        self,
        *args,
        item: OneTimePassword = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(OneTimePasswordRepository, self).__init__(
            *args,
            model=OneTimePassword,
            item=item,
            many=many,
            item_list=item_list,
            **kwargs,
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def send_email_otp(user):
        email = user.email
        subject = "Verification OTP"
        code = random_string_generator(length=6, alphabets=True)
        message = f"{code} is your email verification code for ShareBuddy."
        expiry_date = timezone.now() + relativedelta(minutes=10)
        otp = OneTimePassword.objects.create(
            key_name=OTPKeyNameTypes.EMAIL,
            key_value=email,
            password=code,
            expiry_date=expiry_date,
        )
        success, response = send_email(
            subject=subject,
            message=message,
            receivers=[email],
        )
        return success, response

    @staticmethod
    def send_sms_otp(user):
        mobile_number = user.mobile_number
        code = random_string_generator(length=6, alphabets=True)
        message = f"{code} is your mobile verification code for ShareBuddy."
        expiry_date = timezone.now() + relativedelta(minutes=10)
        otp = OneTimePassword.objects.create(
            key_name=OTPKeyNameTypes.MOBILE,
            key_value=mobile_number,
            password=code,
            expiry_date=expiry_date,
        )
        success, response = send_sms(
            body=message,
            to_=mobile_number,
        )
        return success, response

    @staticmethod
    def verify_email_otp(user, otp):
        otp_object = OneTimePassword.objects.filter(
            key_name=OTPKeyNameTypes.EMAIL, key_value=user.email, password=otp
        ).first()

        if not otp_object:
            return False, "Invalid OTP"
        if otp_object.expiry_date < timezone.now():
            return False, "Otp Expired"
        user.is_email_verified = True
        user.save()
        return True, "Email verified successfully for ShareBuddy."

    @staticmethod
    def verify_sms_otp(user, otp):
        otp_object = OneTimePassword.objects.filter(
            key_name=OTPKeyNameTypes.MOBILE,
            key_value=user.mobile_number,
            password=otp,
        ).first()

        if not otp_object:
            return False, "Invalid OTP"
        if otp_object.expiry_date < timezone.now():
            return False, "Otp Expired"
        user.is_mobile_number_verified = True
        user.save()
        return True, "Mobile Number verified successfully for ShareBuddy."
