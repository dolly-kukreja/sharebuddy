import logging
import re
from rest_framework.decorators import api_view
from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.customuser import CustomUserRepository
from django.contrib.auth.decorators import login_required
from core.serializers.root_serializers import CustomUserSerializer

LOGGER = logging.getLogger(__name__)


class CustomUserController:
    @staticmethod
    @api_view(["POST"])
    def register_user(request):
        post_data = request.data
        LOGGER.info("Check post data: %s", post_data)
        first_name = post_data.get("first_name")
        last_name = post_data.get("last_name")
        email = post_data.get("email")
        mobile_number = post_data.get("mobile_number")
        password = post_data.get("password")
        confirm_password = post_data.get("confirm_password")
        dob = post_data.get("dob")
        profile_photo = post_data.get("profile_photo")
        if (
            not first_name
            or not last_name
            or not email
            or not mobile_number
            or not password
            or not confirm_password
        ):
            return BadRequestJSONResponse(message="Invalid Params.")

        if not re.search(r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$", email):
            return BadRequestJSONResponse(message="Enter a valid email address")

        if not re.match(r"\d{10}$", mobile_number):
            return BadRequestJSONResponse(message="Enter a valid mobile number")

        if password != confirm_password:
            return BadRequestJSONResponse(message="Passwords does not match.")

        if len(password) < 8 or not password.isalnum():
            return BadRequestJSONResponse(
                message="Invalid Password. Password should be greater than 8 digits and should contain atleast one character and atleast one number."
            )

        success, response = CustomUserRepository.create_user(
            firstname=first_name,
            lastname=last_name,
            email=email,
            mobile_number=mobile_number,
            password=password,
            dob=dob,
            profile_photo=profile_photo,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse("User Registered Successfully.")

    @staticmethod
    @api_view(["POST"])
    @login_required
    def update_user_details(request):
        user = request.user
        post_data = request.data
        LOGGER.info("Check post data for user: %s, %s", post_data, user)

        success, response = CustomUserRepository.update_basic_details(
            user=user, post_data=post_data
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    def login_user(request):
        post_data = request.data
        username = post_data.get("username")
        password = post_data.get("password")
        if not username or not password:
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = CustomUserRepository.login_user(request, username, password)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    def change_email_mobile(request):
        post_data = request.data
        LOGGER.info("Check post data: %s", post_data)
        old_email = post_data.get("old_email")
        new_email = post_data.get("new_email")
        mobile_number = post_data.get("mobile_number")
        if not old_email or (not new_email and not mobile_number):
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = CustomUserRepository.change_email_mobile(
            old_email, new_email, mobile_number
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_user_details(request):
        user = request.user
        return SuccessJSONResponse(CustomUserSerializer(user).data)
