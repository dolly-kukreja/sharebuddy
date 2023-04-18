from typing import Any

from django.db.models import Q
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from core.constants import FriendRequestStatus
from core.models import (
    Address,
    CustomUser,
    FriendRequestModel,
    Product,
    Quote,
    Notification,
    Message,
)


class CustomUserSerializer(ModelSerializer):
    """
    Serialize CustomUser model.
    """

    friend_status = SerializerMethodField()

    def get_friend_status(self, user: CustomUser) -> Any:
        current_user = self.context.get("current_user")
        if current_user:
            friend_request_object = FriendRequestModel.objects.filter(
                Q(
                    sender=user,
                    receiver=current_user,
                )
                | Q(
                    sender=current_user,
                    receiver=user,
                )
            ).first()
            if not friend_request_object or int(friend_request_object.status) in (
                FriendRequestStatus.REMOVE,
                FriendRequestStatus.REJECT,
            ):
                return "non_friends"
            if int(friend_request_object.status) == FriendRequestStatus.PENDING:
                return "pending"
            if int(friend_request_object.status) == FriendRequestStatus.ACCEPT:
                return "friends"

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
            "friend_status",
        )


class CustomUserShortSerializer(ModelSerializer):
    """
    Serialize CustomUser Model(But with only required fields)
    """

    full_name = SerializerMethodField()
    user_id = SerializerMethodField()
    profile_photo = SerializerMethodField()

    def get_user_id(self, user: CustomUser) -> Any:
        """
        Get user id
        """
        return user.user_id

    def get_full_name(self, user: CustomUser) -> Any:
        """
        Get user full name
        """
        return user.full_name

    def get_profile_photo(self, user: CustomUser) -> Any:
        """
        Get user profile photo
        """
        return str(user.profile_photo.url) if user.profile_photo else None

    class Meta:
        model = CustomUser
        fields = ("user_id", "full_name", "profile_photo")


class AddressSerializer(ModelSerializer):
    """
    Serialize Address model.
    """

    user = CustomUserShortSerializer()

    class Meta:
        model = Address
        fields = (
            "user",
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

    user = CustomUserShortSerializer()

    class Meta:
        model = Product
        fields = (
            "product_id",
            "user",
            "category",
            "name",
            "description",
            "photo",
            "rent_amount",
            "ratings",
            "is_available",
            "is_active",
            "created_date",
            "updated_date",
        )


class FriendRequestSerializer(ModelSerializer):
    """
    Serializer FriendRequest Model
    """

    sender = CustomUserShortSerializer()

    class Meta:
        model = FriendRequestModel
        fields = (
            "sender",
            "status",
            "created_date",
            "updated_date",
        )


# class FriendSerializer(ModelSerializer):
#     friend_list = SerializerMethodField()


#     def get_friend_list(self, friends: Friends) -> Any:
#         """
#         Get user id
#         """
#         friends_dict = []
#         for user_id in literal_eval(friends.friends_list):
#             friend_obj = CustomUser.objects.filter(user_id=str(user_id)).first()
#             friends_dict.append([friend_obj.full_name,
#                          str(friend_obj.profile_photo.url) if friend_obj.profile_photo else None,
#                          friend_obj.user_id])
#         return friends_dict

#     class Meta:
#         model = Friends
#         fields = (
#             "friend_list",
#         )


class QuoteSerializer(ModelSerializer):
    """
    Quote model Serializer.
    """

    customer = CustomUserShortSerializer()
    owner = CustomUserShortSerializer()
    last_updated_by = CustomUserShortSerializer()
    product = ProductSerializer()

    class Meta:
        model = Quote
        fields = (
            "quote_id",
            "product",
            "customer",
            "owner",
            "last_updated_by",
            "status",
            "exchange_type",
            "rent_amount",
            "deposit_amount",
            "is_rent_paid",
            "is_deposit_paid",
            "meetup_point",
            "from_date",
            "to_date",
            "approved_by_customer",
            "approved_by_owner",
            "rejected_by_customer",
            "rejected_by_owner",
            "is_closed",
            "remarks",
            "type_change_history",
            "remarks_history",
            "created_date",
            "updated_date",
        )


class NotificationSerializer(ModelSerializer):
    """
    Notification Model Serializer
    """

    user = CustomUserShortSerializer()

    class Meta:
        model = Notification
        fields = (
            "id",
            "user",
            "text",
            "status",
            "channel",
            "type",
            "type_id",
            "created_date",
            "updated_date",
        )


class MessageSerializer(ModelSerializer):
    """
    Notification Model Serializer
    """

    sender = CustomUserShortSerializer()
    receiver = CustomUserShortSerializer()

    class Meta:
        model = Message
        fields = (
            "sender",
            "receiver",
            "message",
            "is_read",
            "created_date",
            "updated_date",
            )
