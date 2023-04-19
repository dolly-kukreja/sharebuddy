import logging

from django.db.models import QuerySet, Q

from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_none
from core.models import CustomUser, Message, Friends
from core.serializers.root_serializers import MessageSerializer
from ast import literal_eval
LOGGER = logging.getLogger(__name__)


class MessageRepository:
    def __init__(
            self,
            *args,
            item: Message = None,
            many: bool = False,
            item_list: QuerySet = None,
            **kwargs,
    ):
        super(MessageRepository, self).__init__(
            *args,
            model=Message,
            item=item,
            many=many,
            item_list=item_list,
            **kwargs,
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_unread_count(sender, receiver):
        message_list_object = Message.objects.filter(
            sender=sender,
            receiver=receiver,
            is_read=False).count()
        return message_list_object

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def message_list(sender_user, receiver_id, message, request_method):
        # check if receiver exist
        receiver_object = get_or_none(CustomUser, user_id=receiver_id)
        if not receiver_object:
            return False, "Invalid Receiver ID."
        if request_method == 'POST':
            if not message:
                return True, "Please Type Message."
            send_message = Message.objects.create(
                sender=sender_user,
                receiver=receiver_object,
                message=message,
                is_read=False
            )
            send_message.save()
            message_list_object = Message.objects.filter(
                Q(
                    sender=sender_user,
                    receiver=receiver_object,
                )
                | Q(
                    sender=receiver_object,
                    receiver=sender_user,
                )
            ).all()
            message_data = MessageSerializer(message_list_object, many=True).data
            return True, message_data
        if request_method == 'GET':
            message_list_object = Message.objects.filter(
                Q(
                    sender=sender_user,
                    receiver=receiver_object,
                )
                | Q(
                    sender=receiver_object,
                    receiver=sender_user,
                )
            ).all()
            if not message_list_object:
                return True, "No messages found."
            message_list_object.filter(receiver=sender_user).update(is_read=True)
            message_data = MessageSerializer(message_list_object, many=True).data
            return True, message_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_last_message(current_user):
        friend_list_object = Friends.objects.filter(user=current_user).first()
        if not friend_list_object or not friend_list_object.friends_list:
            return True, "No Friends Found."
        message_data = []
        friends_list = literal_eval(friend_list_object.friends_list)
        for friend in friends_list:
            friend_object = get_or_none(CustomUser, user_id=friend)
            message_list_object = Message.objects.filter(
                Q(
                    sender=current_user,
                    receiver=friend_object,
                )
                | Q(
                    sender=friend_object,
                    receiver=current_user,
                )
            ).order_by('-created_date').first()
            unread_count = 0
            if not message_list_object:
                message_data.append(
                    {
                        "friend_name": friend_object.full_name,
                        "photo": str(friend_object.profile_photo.url)
                        if friend_object.profile_photo
                        else None,
                        "user_id": friend_object.user_id,
                        "last_message": "",
                        "timestamp": "",
                        "unread_count": unread_count
                    }
                )
            else:
                if message_list_object.receiver == current_user:
                    unread_count = MessageRepository.get_unread_count(sender=friend_object, receiver=current_user)
                message_data.append(
                    {
                        "friend_name": friend_object.full_name,
                        "photo": str(friend_object.profile_photo.url)
                        if friend_object.profile_photo
                        else None,
                        "user_id": friend_object.user_id,
                        "last_message": message_list_object.message,
                        "timestamp": message_list_object.created_date,
                        "unread_count": unread_count
                    }
                )
        return True, message_data



