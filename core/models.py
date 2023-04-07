import re
import random
from django.db import models
from django.db.models import (
    Model,
    IntegerField,
    CharField,
    BooleanField,
    EmailField,
    ImageField,
    DateField,
    ForeignKey,
    DateTimeField,
)
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from datetime import datetime
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from core.constants import OTPKeyNameTypes, FriendRequestStatus

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password,
        first_name=None,
        last_name=None,
        mobile_number=None,
        is_mobile_number_verified=False,
    ):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=mobile_number,
            is_mobile_number_verified=is_mobile_number_verified,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """

        if not re.search(r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$", email):
            raise ValueError("Invalid email address")
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def generate_user_id():
    user_id = "".join(
        [random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVXYZ") for i in range(11)]
    )
    return user_id


def get_profile_photo_filepath_with_name(instance, name):
    date = datetime.strftime(datetime.now(), "%Y_%m_%d_%H_%M_%S")
    ext = name.split(".")[-1]
    return "profile_photo/" + date + instance.user_id + "." + ext


# CUSTOM USER


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = CharField(
        max_length=255, editable=False, default=generate_user_id, unique=True, null=True
    )
    first_name = CharField(max_length=700, null=True, blank=True)
    last_name = CharField(max_length=700, null=True, blank=True)
    mobile_number = CharField(max_length=15, editable=True, null=True)
    is_mobile_number_verified = BooleanField(default=False)
    email = EmailField(verbose_name="email address", max_length=255, unique=True)
    is_email_verified = BooleanField(default=False)
    dob = DateField(null=True)
    profile_photo = ImageField(
        null=True, blank=True, upload_to=get_profile_photo_filepath_with_name
    )
    is_active = BooleanField(default=True, verbose_name="Active")
    is_staff = BooleanField(default=False, verbose_name="Staff")
    is_superuser = BooleanField(default=False, verbose_name="SuperUser")
    ratings = IntegerField(default=2)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELD = ["email"]
    objects = CustomUserManager()

    def __str__(
        self,
    ):
        return str(self.email)


class Address(Model):
    user = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="address_user")
    line1 = CharField(max_length=300)
    line2 = CharField(max_length=300, null=True, blank=True)
    city = CharField(max_length=200, default="MUMBAI")
    state = CharField(max_length=200, default="MAHARASHTRA")
    country = CharField(max_length=200, default="INDIA")
    landmark = CharField(max_length=100, null=True, blank=True)
    pincode = CharField(max_length=6, null=True, blank=True)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(
        self,
    ):
        return str(self.user.email) + "-" + self.state


class OneTimePassword(Model):
    key_name_choices = (
        (OTPKeyNameTypes.MOBILE, "MOBILE"),
        (OTPKeyNameTypes.EMAIL, "EMAIL"),
    )
    # purpose_choices = (
    #     (OTPPurposeTypes.EMAIL_VERIFICATION, OTPPurposeTypes.EMAIL_VERIFICATION),
    #     (
    #         OTPPurposeTypes.MOBILE_NUMBER_VERIFICATION,
    #         OTPPurposeTypes.MOBILE_NUMBER_VERIFICATION,
    #     ),
    #     (OTPPurposeTypes.BUY_CONFIMATION, OTPPurposeTypes.BUY_CONFIMATION),
    #     (OTPPurposeTypes.SELL_CONFIRMATION, OTPPurposeTypes.SELL_CONFIRMATION),
    #     (OTPPurposeTypes.PASSWORD_RESET, OTPPurposeTypes.PASSWORD_RESET),
    #     (OTPPurposeTypes.LOGIN, OTPPurposeTypes.LOGIN),
    # )
    key_name = CharField(max_length=15, choices=key_name_choices)
    key_value = CharField(max_length=256)  # Email or Mobile Number
    password = CharField(max_length=33)
    # purpose = CharField(
    #     max_length=33,
    #     choices=purpose_choices,
    #     default=OTPPurposeTypes.MOBILE_NUMBER_VERIFICATION,
    # )
    expiry_date = DateTimeField(null=True, blank=True)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return str(self.key_name) + "-" + str(self.key_value)


# friend request model
class FriendRequestModel(Model):
    status_choices = (
        (FriendRequestStatus.ACCEPT, "Accept"),
        (FriendRequestStatus.REJECT, "Reject"),
        (FriendRequestStatus.PENDING, "Pending")
    )
    sender_id = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sender_id")
    receiver_id = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="receiver_id")
    status = CharField(max_length=100, null=True, blank=True, choices=status_choices, default=FriendRequestStatus.PENDING)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

