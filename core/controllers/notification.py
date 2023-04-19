from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.notification import NotificationRepository


class NotificationController:
    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_in_app_notifications(request):
        user = request.user
        success, response = NotificationRepository.get_in_app_notifications(
            current_user=user
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def mark_notification_as_read(request):
        notification_id = request.data.get("notification_id")
        if not notification_id:
            return False, "Invalid Params"
        success, response = NotificationRepository.mark_notification_as_read(
            notification_id=notification_id
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
