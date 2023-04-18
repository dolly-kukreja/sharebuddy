from rest_framework.decorators import api_view
from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.message import MessageRepository
from django.contrib.auth.decorators import login_required


class MessageController:
    @staticmethod
    @api_view(["POST", "GET"])
    @login_required
    def message_list(request):
        sender_user = request.user
        post_data = request.data
        receiver_id = post_data.get("receiver_id")
        message = post_data.get("message")

        if not receiver_id or len(receiver_id) != 10:
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = MessageRepository.message_list(
            sender_user=sender_user,
            receiver_id=receiver_id,
            message=message,
            request_method=request.method,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
