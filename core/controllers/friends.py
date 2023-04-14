from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.friends import FriendsRepository


class FriendsController:
    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_friends(request):
        current_user = request.user
        success, response = FriendsRepository.get_friends(current_user=current_user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def remove_friend(request):
        current_user = request.user
        post_data = request.data
        friend_id = post_data.get("friend_id")
        if not friend_id or len(friend_id) != 10:
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = FriendsRepository.remove_friend(
            current_user=current_user, friend_id=friend_id
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
