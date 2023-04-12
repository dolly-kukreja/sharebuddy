from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
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
    @login_required
    def verify_email_otp(request):
        user = request.user
        otp = request.data.get("otp")
        if not otp:
            return BadRequestJSONResponse(message="Please pass otp.")
        success, response = OneTimePasswordRepository.verify_email_otp(user, otp)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def verify_sms_otp(request):
        user = request.user
        otp = request.data.get("otp")
        if not otp:
            return BadRequestJSONResponse(message="Please pass otp.")
        success, response = OneTimePasswordRepository.verify_sms_otp(user, otp)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
