import logging
import re
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.db.models import QuerySet

from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_none
from core.models import CustomUser, Wallet
from core.repositories.otp import OneTimePasswordRepository
from core.serializers.root_serializers import CustomUserSerializer
from core.serializers.token_serializers import get_token_pair

LOGGER = logging.getLogger(__name__)


class CustomUserRepository:
    def __init__(
        self,
        *args,
        item: CustomUser = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(CustomUserRepository, self).__init__(
            *args, model=CustomUser, item=item, many=many, item_list=item_list, **kwargs
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def create_user(
        firstname, lastname, email, mobile_number, password, dob, profile_photo
    ):
        existing_user = CustomUser.objects.filter(email=email)
        if existing_user:
            return False, "Email already exists."
        # Creating User Object
        new_user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname,
            mobile_number=mobile_number,
        )
        if dob:
            dob = datetime.strptime(dob, "%d/%m/%Y")
            new_user.dob = dob
        if profile_photo:
            new_user.profile_photo = profile_photo
        new_user.save()
        LOGGER.info("Check new user: %s", new_user)
        # Sending OTPs
        success, response = OneTimePasswordRepository.send_email_otp(new_user)
        LOGGER.info("Send Email OTP success and response: %s, %s", success, response)
        success, response = OneTimePasswordRepository.send_sms_otp(new_user)
        LOGGER.info("Send SMS OTP success and response: %s, %s", success, response)
        Wallet.objects.create(user=new_user)
        tokens = get_token_pair(new_user)
        LOGGER.info("token: %s", tokens)
        tokens.update({"is_admin": new_user.is_superuser})
        return True, tokens

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def login_user(request, email, password):
        authentication = authenticate(username=email, password=password)
        if authentication is None:
            return False, "Invalid credentials."
        login(request, authentication)
        user = request.user
        tokens = get_token_pair(user)
        LOGGER.info("token: %s", tokens)
        tokens.update({"is_admin": user.is_superuser})
        return True, tokens

    @staticmethod
    def change_password(user, new_password):
        user.set_password(new_password)
        user.save()
        return True, "Password updated successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_basic_details(user, post_data):
        first_name = post_data.get("first_name")
        last_name = post_data.get("last_name")
        mobile_number = post_data.get("mobile_number")
        email = post_data.get("email")
        dob = post_data.get("dob")
        profile_photo = post_data.get("photo")

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name

        if email:
            if not re.search(
                r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$", email
            ):
                return False, "Enter a valid email address"
            user.email = email
            user.is_email_verified = False

        if mobile_number:
            if not re.match(r"\d{10}$", mobile_number):
                return False, "Enter a valid mobile number"
            user.mobile_number = mobile_number
            user.is_mobile_number_verified = False

        if dob:
            dob = datetime.strptime(dob, "%d/%m/%Y")
            user.dob = dob

        if profile_photo:
            user.profile_photo = profile_photo
        user.save()
        return True, "User Details Updated Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_user_profile(user_id):
        user = get_or_none(CustomUser, user_id=user_id)
        if not user:
            return False, "Invalid User ID."
        user_details = CustomUserSerializer(user).data
        return True, user_details

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_all_users(current_user):
        all_users = (
            CustomUser.objects.filter(is_active=True)
            .exclude(is_superuser=True)
            .order_by("first_name")
        )
        context = {"current_user": current_user}
        user_details = CustomUserSerializer(all_users, context=context, many=True).data
        return True, user_details

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def delete_user(user_id):
        user = get_or_none(CustomUser, user_id=user_id)
        if not user:
            return False, "Invalid User ID."
        user.is_active = False
        user.save()
        return True, "User Deleted Successfully."
