from rest_framework.decorators import api_view
from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse

from django.contrib.auth.decorators import login_required
from core.models import CustomUser
from core.repositories.otp import OneTimePasswordRepository


class OneTimePasswordController:
    @staticmethod
    @api_view(["POST"])
    @login_required
    def send_email_otp(request):
        user = request.user
        success, response = OneTimePasswordRepository.send_email_otp(user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def send_sms_otp(request):
        user = request.user
        success, response = OneTimePasswordRepository.send_sms_otp(user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    def verify_email_otp(request):
        user = request.user
        if request.user.is_anonymous:
            email = request.data.get("email")
            if not email:
                return BadRequestJSONResponse(message="Please add email.")
            user = CustomUser.objects.get(email=email)
            if not user:
                return BadRequestJSONResponse(message="Invalid Email ID.")
        otp = request.data.get("otp")
        if not otp:
            return BadRequestJSONResponse(message="Please pass otp.")
        success, response = OneTimePasswordRepository.verify_email_otp(user, otp)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    def verify_sms_otp(request):
        user = request.user
        if request.user.is_anonymous:
            mobile_number = request.data.get("mobile_number")
            if not mobile_number:
                return BadRequestJSONResponse(message="Please add mobile number.")
            user = CustomUser.objects.get(mobile_number=mobile_number)
            if not user:
                return BadRequestJSONResponse(message="Invalid Mobile Number.")
        otp = request.data.get("otp")
        if not otp:
            return BadRequestJSONResponse(message="Please pass otp.")
        success, response = OneTimePasswordRepository.verify_sms_otp(user, otp)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
