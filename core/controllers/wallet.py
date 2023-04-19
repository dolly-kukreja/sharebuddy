from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.wallet import WalletRepository


class WalletController:
    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_wallet_balance(request):
        user = request.user
        success, response = WalletRepository.get_wallet_balance(user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
