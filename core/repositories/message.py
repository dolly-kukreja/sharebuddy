import logging

from django.db.models import QuerySet, Q

from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_none
from core.models import CustomUser, Message
from core.serializers.root_serializers import MessageSerializer

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
            message_list_object.filter(receiver=sender_user).update(is_read=True)
            message_data = MessageSerializer(message_list_object, many=True).data
            return True, message_data
