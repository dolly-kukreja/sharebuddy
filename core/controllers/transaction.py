from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required, user_passes_test

from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.transaction import TransactionRepository


class TransactionController:
    @staticmethod
    @api_view(["GET"])
    @login_required
    @user_passes_test(lambda u: u.is_superuser)
    def get_all_transactions(request):
        success, response = TransactionRepository.get_all_transactions()
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_my_transactions(request):
        success, response = TransactionRepository.get_my_transactions(request.user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
