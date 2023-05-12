import logging
import re

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import api_view

from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.customuser import CustomUserRepository
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

        if len(password) < 8:
            return BadRequestJSONResponse(
                message="Invalid Password. Password should be greater than 8 digits."
            )

        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        pat = re.compile(reg)
        mat = re.search(pat, password)
        if not mat:
            return BadRequestJSONResponse(
                "Password should contain one numeric, one upper character and one special character."
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
        return SuccessJSONResponse(response)

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
        email = post_data.get("email")
        password = post_data.get("password")
        if not email or not password:
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = CustomUserRepository.login_user(request, email, password)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_user_details(request):
        user = request.user
        return SuccessJSONResponse(CustomUserSerializer(user).data)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_user_profile(request):
        user_id = request.GET.get("user_id")
        success, response = CustomUserRepository.get_user_profile(user_id)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_all_users(request):
        success, response = CustomUserRepository.get_all_users(request.user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def change_password(request):
        user = request.user
        post_data = request.data
        old_password = post_data.get("old_password")
        new_password = post_data.get("new_password")
        confirm_password = post_data.get("confirm_password")

        authentication = authenticate(username=user.email, password=old_password)
        if not authentication:
            return BadRequestJSONResponse(message="Incorrect Password.")

        if new_password != confirm_password:
            return BadRequestJSONResponse(message="Passwords does not match.")

        if len(new_password) < 8:
            return BadRequestJSONResponse(
                message="Invalid Password. Password should be greater than 8 digits."
            )

        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        pat = re.compile(reg)
        mat = re.search(pat, new_password)
        if not mat:
            return BadRequestJSONResponse(
                "Password should contain one numeric, one upper character and one special character."
            )

        success, response = CustomUserRepository.change_password(user, new_password)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    @user_passes_test(lambda u: u.is_superuser)
    def delete_user(request):
        post_data = request.data
        user_id = post_data.get("user_id")
        success, response = CustomUserRepository.delete_user(user_id)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
