from typing import Any
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from core.models import CustomUser, Address, OneTimePassword


class CustomUserSerializer(ModelSerializer):
    """
    Serialize CustomUser model.
    """

    class Meta:
        model = CustomUser
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "mobile_number",
            "is_mobile_number_verified",
            "is_email_verified",
            "dob",
            "profile_photo.url",
            "is_active",
            "is_staff",
            "is_superuser",
            "ratings",
            "created_date",
            "updated_date",
        )


class AddressSerializer(ModelSerializer):
    """
    Serialize Address model.
    """

    user_id = SerializerMethodField()

    def get_user_id(self, address: Address) -> Any:
        """
        Get user id
        """
        return address.user.user_id

    class Meta:
        model = Address
        fields = (
            "user_id",
            "id",
            "line1",
            "line2",
            "city",
            "state",
            "country",
            "landmark",
            "pincode",
        )
