from django.urls import path
from core.views import (
    CustomUserController,
    OneTimePasswordController,
    AddressController,
)

urlpatterns = [
    # CustomUser URLs
    path("register", CustomUserController.register_user, name="register"),
    path("login", CustomUserController.login_user, name="login"),
    path(
        "update_user_details",
        CustomUserController.update_user_details,
        name="update_user_details",
    ),
    path(
        "change_email_mobile",
        CustomUserController.change_email_mobile,
        name="change_email_mobile",
    ),
    path(
        "get_user_details",
        CustomUserController.get_user_details,
        name="get_user_details",
    ),
    # OTP URLs
    path(
        "send_email_otp",
        OneTimePasswordController.send_email_otp,
        name="send_email_otp",
    ),
    path("send_sms_otp", OneTimePasswordController.send_sms_otp, name="send_sms_otp"),
    path(
        "verify_email_otp",
        OneTimePasswordController.verify_email_otp,
        name="verify_email_otp",
    ),
    path(
        "verify_sms_otp",
        OneTimePasswordController.verify_sms_otp,
        name="verify_sms_otp",
    ),
    # Address URLs
    path(
        "add_address",
        AddressController.add_address,
        name="add_address",
    ),
    path(
        "update_address",
        AddressController.update_address,
        name="update_address",
    ),
    path(
        "get_user_address",
        AddressController.get_user_address,
        name="get_user_address",
    ),
]
