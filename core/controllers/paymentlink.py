from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from core.constants import PaymentLinkStatus

from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.models import PaymentLink, Quote
from core.repositories.paymentlink import PaymentLinkRepostitory
from core.repositories.quote import QuoteRepository


class PaymentLinkController:
    @staticmethod
    @api_view(["POST"])
    def payment_link_webhook(request):
        request_data = request.data
        success, response = PaymentLinkRepostitory.payment_link_webhook(request_data)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse("Payment Link Updated Successfully.")
