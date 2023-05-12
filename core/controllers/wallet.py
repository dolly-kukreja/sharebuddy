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

    @staticmethod
    @api_view(["POST"])
    @login_required
    def debit_wallet_cash(request):
        user = request.user
        amount = request.data.get("amount")
        if not amount:
            return BadRequestJSONResponse(response="Invalid Params")
        success, response = WalletRepository.debit_wallet_cash(user=user, amount=amount)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
