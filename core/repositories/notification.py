import logging
from django.db.models import QuerySet
from core.constants import NotificationStatus
from core.helpers.decorators import handle_unknown_exception

from core.models import Notification
from core.serializers.root_serializers import NotificationSerializer

LOGGER = logging.getLogger(__name__)


class NotificationRepository:
    def __init__(
        self,
        *args,
        item: Notification = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(NotificationRepository, self).__init__(
            *args,
            model=Notification,
            item=item,
            many=many,
            item_list=item_list,
            **kwargs,
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_in_app_notifications(current_user):
        notifications = current_user.user_notifications.all().order_by("-created_date")
        if not notifications:
            return True, "Notifications not found."
        unread_count = notifications.filter(status=NotificationStatus.UNREAD).count()
        notifications_data = NotificationSerializer(notifications, many=True).data
        response = {"unread_count": unread_count, "data": notifications_data}
        return True, response

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def mark_notification_as_read(notification_id):
        notification = Notification.objects.filter(id=notification_id).first()
        if not notification:
            return False, "Invalid Notification ID."
        notification.status = NotificationStatus.READ
        notification.save()
        return True, "Notification Updated Successfully."
