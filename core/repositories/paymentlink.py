import json
import logging

from django.db.models import QuerySet

from core.constants import PaymentLinkStatus, PaymentLinkTransactionTypes
from core.helpers.decorators import handle_unknown_exception
from core.models import CustomUser, PaymentLink, Quote, generate_unique_id
from core.services.cashfree import create_payment_link

LOGGER = logging.getLogger(__name__)


class PaymentLinkRepostitory:
    def __init__(
        self,
        *args,
        item: PaymentLink = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(PaymentLinkRepostitory, self).__init__(
            *args,
            model=PaymentLink,
            item=item,
            many=many,
            item_list=item_list,
            **kwargs,
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def send_payment_link(payment_type: str, quote: Quote, user: CustomUser):
        if payment_type == PaymentLinkTransactionTypes.RENT:
            payment_amount = quote.rent_amount + quote.deposit_amount
        if payment_type == PaymentLinkTransactionTypes.DEPOSIT:
            payment_amount = quote.deposit_amount
        payment_link = generate_unique_id()
        payment_purpose = str(payment_type) + " for " + str(quote.product.name)
        success, response = create_payment_link(
            link_id=payment_link,
            link_amount=payment_amount,
            link_purpose=payment_purpose,
            customer=user,
            expiry_time=quote.from_date.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
        )
        if not success:
            return False, response
        response_content = json.loads(response.text)
        payment_link_url = response_content.get("link_url")
        if not success:
            return False, response
        PaymentLink.objects.create(
            user=user,
            quote=quote,
            link_id=payment_link,
            link_amount=payment_amount,
            link_purpose=payment_purpose,
            expiry_date=quote.from_date,
            link_url=payment_link_url,
        )
        return True, "Payment Link Sent Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def payment_link_webhook(request_data):
        print(request_data, "<<<<")
        link_id = request_data.get("data").get("link_id")
        if not link_id:
            link_id = request_data.get("data").get("order").get("order_tags").get("link_id")
        link_status = request_data.get("data").get("link_status")
        if not link_status:
            link_status = request_data.get("data").get("payment").get("payment_status")
        payment_link_object = PaymentLink.objects.get(link_id=link_id)
        payment_link_object.status = link_status
        payment_link_object.save()
        from core.repositories.quote import QuoteRepository

        if link_status == PaymentLinkStatus.PAID or link_status == "SUCCESS":
            success, response = QuoteRepository.after_payment_process(
                payment_link_object.quote, payment_link_object.link_amount
            )
        elif link_status == PaymentLinkStatus.EXPIRED:
            success, response = QuoteRepository.close_quote_with_failed_payment(
                payment_link_object.quote
            )
        if not success:
            return False, response
        return True, response
