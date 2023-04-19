from rest_framework.decorators import api_view
from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.message import MessageRepository
from django.contrib.auth.decorators import login_required


class MessageController:
    @staticmethod
    @api_view(["POST", "GET"])
    @login_required
    def message_list(request):
        if request.method == 'GET':
            receiver_id = request.GET.get("receiver_id")
            message = None
        elif request.method == 'POST':
            post_data = request.data
            receiver_id = post_data.get("receiver_id")
            message = post_data.get("message")
        sender_user = request.user

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

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_last_message(request):
        current_user = request.user
        success, response = MessageRepository.get_last_message(
            current_user=current_user,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
