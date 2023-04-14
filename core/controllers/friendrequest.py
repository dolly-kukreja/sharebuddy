from rest_framework.decorators import api_view
from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.friendrequest import FriendRequestRepository
from django.contrib.auth.decorators import login_required
from core.constants import FriendRequestStatus


class FriendRequestController:
    @staticmethod
    @api_view(["POST"])
    @login_required
    def send_friend_request(request):
        sender_user = request.user
        post_data = request.data
        receiver_id = post_data.get("receiver_id")

        if not receiver_id or len(receiver_id) != 10:
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = FriendRequestRepository.send_friend_request(
            sender_user=sender_user,
            receiver_id=receiver_id,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def action_on_friend_request(request):
        receiver_user = request.user
        post_data = request.data
        sender_id = post_data.get("sender_id")
        action = int(post_data.get("action"))
        if (
            not sender_id
            or len(sender_id) != 10
            or not action
            or action not in (FriendRequestStatus.ACCEPT, FriendRequestStatus.REJECT)
        ):
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = FriendRequestRepository.action_on_friend_request(
            receiver_user=receiver_user, sender_id=sender_id, action=action
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_friend_request(request):
        receiver_user = request.user
        success, response = FriendRequestRepository.get_friend_request(
            receiver_user=receiver_user
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
