import logging

from django.db.models import QuerySet, Q

from core.constants import FriendRequestStatus
from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_none
from core.models import FriendRequestModel, CustomUser, Friends
from core.repositories.friends import FriendsRepository
from core.serializers.root_serializers import FriendRequestSerializer

LOGGER = logging.getLogger(__name__)


class FriendRequestRepository:
    def __init__(
        self,
        *args,
        item: FriendRequestModel = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(FriendRequestRepository, self).__init__(
            *args,
            model=FriendRequestModel,
            item=item,
            many=many,
            item_list=item_list,
            **kwargs,
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def send_friend_request(sender_user, receiver_id):
        # check if receiver exist
        receiver_object = get_or_none(CustomUser, user_id=receiver_id)
        if not receiver_object:
            return False, "Invalid Receiver ID."
        if receiver_id == sender_user.user_id:
            return False, "Cannot send request to self"
        friend_request_object = FriendRequestModel.objects.filter(
            Q(
                sender=sender_user.id,
                receiver=receiver_object.id,
                status__in=[FriendRequestStatus.ACCEPT, FriendRequestStatus.PENDING],
            )
            | Q(
                sender=receiver_object.id,
                receiver=sender_user.id,
                status__in=[FriendRequestStatus.ACCEPT, FriendRequestStatus.PENDING],
            )
        )

        if friend_request_object:
            return False, "Friendship already exist or in Pending Stage."
        friend_request_object_reject = FriendRequestModel.objects.filter(
            sender=sender_user,
            receiver=receiver_object,
            status__in=[FriendRequestStatus.REJECT, FriendRequestStatus.REMOVE],
        ).first()
        if friend_request_object_reject:
            friend_request_object_reject.status = FriendRequestStatus.PENDING
            friend_request_object_reject.save()
            return True, "Friend Request Sent Successfully."
        friend_request_object = FriendRequestModel(
            sender=sender_user,
            receiver=receiver_object,
            status=FriendRequestStatus.PENDING,
        )
        friend_request_object.save()
        return True, "Friend Request Sent Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def action_on_friend_request(action, sender_id, receiver_user):
        # check if receiver exist
        sender_object = get_or_none(CustomUser, user_id=sender_id)
        if not sender_object:
            return False, "Invalid Sender ID."

        friend_request_object = FriendRequestModel.objects.filter(
            sender=sender_object,
            receiver=receiver_user,
            status=FriendRequestStatus.PENDING,
        ).first()
        if not friend_request_object:
            return False, "No Such Request Found."
        friend_request_object.status = int(action)
        friend_request_object.save()

        if action == FriendRequestStatus.ACCEPT:
            FriendsRepository.add_friend_in_db(user=receiver_user, friend_id=sender_id)
            FriendsRepository.add_friend_in_db(
                user=sender_object, friend_id=receiver_user.user_id
            )
        friend_status_dict = {
            key: value
            for key, value in FriendRequestStatus.__dict__.items()
            if not key.startswith("__") and not callable(key)
        }
        action_keyword = [k for k, v in friend_status_dict.items() if v == action]
        return True, "Friend Request " + action_keyword[0].lower() + "ed Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_friend_request(receiver_user):
        # check if receiver exist
        friend_request_object = FriendRequestModel.objects.filter(
            receiver=receiver_user, status=FriendRequestStatus.PENDING
        )
        if not friend_request_object:
            return True, "No Pending Friend Requests."
        friend_requests_data = FriendRequestSerializer(
            friend_request_object, many=True
        ).data
        return True, friend_requests_data
