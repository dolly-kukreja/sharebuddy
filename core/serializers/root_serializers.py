from typing import Any
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from core.models import CustomUser, Address, Product, FriendRequestModel


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
            "profile_photo",
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


class ProductSerializer(ModelSerializer):
    """
    Serialize Product Model
    """

    user_id = SerializerMethodField()

    def get_user_id(self, product: Product) -> Any:
        """
        Get user id
        """
        return product.user.user_id

    class Meta:
        model = Product
        fields = (
            "product_id",
            "user_id",
            "category",
            "name",
            "description",
            "photo",
            "price",
            "ratings",
            "is_available",
            "is_active",
            "created_date",
            "updated_date",
        )


class FriendRequestSerializer(ModelSerializer):

    full_name = SerializerMethodField()
    user_id = SerializerMethodField()
    profile_photo = SerializerMethodField()

    def get_user_id(self, friendrequest: FriendRequestModel) -> Any:
        """
        Get user id
        """
        return friendrequest.sender_id.user_id

    def get_full_name(self, friendrequest: FriendRequestModel) -> Any:
        """
        Get user full name
        """
        return friendrequest.sender_id.full_name

    def get_profile_photo(self, friendrequest: FriendRequestModel) -> Any:
        """
        Get user profile photo
        """
        return str(friendrequest.sender_id.profile_photo.url)

    class Meta:
        model = FriendRequestModel
        fields = (
            "user_id",
            "full_name",
            "profile_photo",
            "status",
            "created_date",
            "updated_date",
        )
