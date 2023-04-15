import logging
from ast import literal_eval

from django.db.models import QuerySet, Q

from core.constants import FriendRequestStatus
from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_none
from core.models import Friends, CustomUser, FriendRequestModel

LOGGER = logging.getLogger(__name__)


class FriendsRepository:
    def __init__(
        self,
        *args,
        item: Friends = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(FriendsRepository, self).__init__(
            *args, model=Friends, item=item, many=many, item_list=item_list, **kwargs
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_friends(current_user):
        friend_object = Friends.objects.filter(user=current_user).first()
        if not friend_object or not friend_object.friends_list:
            return True, "No Friends Found."
        friends_data = []
        friends_list = literal_eval(friend_object.friends_list)
        for user_id in friends_list:
            friend_obj = CustomUser.objects.filter(user_id=str(user_id)).first()
            friends_data.append(
                {
                    "name": friend_obj.full_name,
                    "photo": str(friend_obj.profile_photo.url)
                    if friend_obj.profile_photo
                    else None,
                    "user_id": friend_obj.user_id,
                }
            )
        return True, friends_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def remove_friend_from_db(user_obj, friend_id):
        friend_list = literal_eval(user_obj.friends_list)
        if friend_id not in friend_list:
            return False, "No Such Friendship Found."
        friend_list.remove(str(friend_id))
        user_obj.friends_list = str(friend_list)
        user_obj.save()
        return True, "Friend Removed Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def remove_friend(current_user, friend_id):
        friend_user_object = get_or_none(CustomUser, user_id=friend_id)
        if not friend_user_object:
            return False, "Invalid Sender ID."
        friend_request_object = FriendRequestModel.objects.filter(
            Q(
                sender=friend_user_object,
                receiver=current_user,
                status=FriendRequestStatus.ACCEPT,
            )
            | Q(
                sender=current_user,
                receiver=friend_user_object,
                status=FriendRequestStatus.ACCEPT,
            )
        ).first()
        if not friend_request_object:
            return False, "No Such Friendship Found."
        friend_request_object.status = FriendRequestStatus.REMOVE
        friend_request_object.save()
        user_friend_list_object = Friends.objects.filter(user=current_user).first()
        if not user_friend_list_object:
            return False, "No Friends Found."
        success, response = FriendsRepository.remove_friend_from_db(
            user_obj=user_friend_list_object, friend_id=friend_id
        )
        if not success:
            return success, response
        sender_friend_list_object = Friends.objects.filter(
            user=friend_user_object
        ).first()
        success, response = FriendsRepository.remove_friend_from_db(
            user_obj=sender_friend_list_object, friend_id=current_user.user_id
        )
        if not success:
            return success, response
        return True, "Friend Removed Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def add_friend_in_db(user, friend_id):
        accept_friend_object = Friends.objects.filter(user=user).first()
        if not accept_friend_object:
            save_friend_object = Friends(user=user, friends_list=str([friend_id]))
            save_friend_object.save()
            return True, "Friend Added Successfully."
        friend_list = literal_eval(accept_friend_object.friends_list)
        friend_list.append(friend_id)
        friend_list_str = str(friend_list)
        accept_friend_object.friends_list = friend_list_str
        accept_friend_object.save()
        return True, "Friend Added Successfully."
