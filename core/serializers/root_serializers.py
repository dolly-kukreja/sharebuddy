from typing import Any
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from core.models import CustomUser, Address, Product, FriendRequestModel, Friends
from django.db.models import Q
from core.constants import FriendRequestStatus


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
            "rent_amount",
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
        return friendrequest.sender.user_id

    def get_full_name(self, friendrequest: FriendRequestModel) -> Any:
        """
        Get user full name
        """
        return friendrequest.sender.full_name

    def get_profile_photo(self, friendrequest: FriendRequestModel) -> Any:
        """
        Get user profile photo
        """
        return (
            str(friendrequest.sender.profile_photo.url)
            if friendrequest.sender.profile_photo
            else None
        )

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
