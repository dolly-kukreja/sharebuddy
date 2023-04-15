import logging
from ast import literal_eval
from datetime import datetime

from django.db.models import QuerySet

from core.constants import ErrorMessages, QuoteExchangeTypes, QuoteStatus
from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_none
from core.models import Notification, Product, Quote
from core.serializers.root_serializers import QuoteSerializer
from core.services.email import send_email

LOGGER = logging.getLogger(__name__)


class QuoteRepository:
    def __init__(
        self,
        *args,
        item: Quote = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(QuoteRepository, self).__init__(
            *args,
            model=Quote,
            item=item,
            many=many,
            item_list=item_list,
            **kwargs,
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def place_quote(
        product_id, customer, exchange_type, from_date, to_date, meetup_point, remarks
    ):
        product = Product.objects.get(product_id=product_id)
        if not product:
            return False, "Product not found."
        from_date_format = datetime.strptime(from_date, "%d/%m/%Y")
        to_date_format = datetime.strptime(to_date, "%d/%m/%Y")
        new_quote = Quote.objects.create(
            product=product,
            owner=product.user,
            customer=customer,
            last_updated_by=customer,
            exchange_type=exchange_type,
            from_date=from_date_format,
            to_date=to_date_format,
            meetup_point=meetup_point,
            remarks=remarks,
            rent_amount=product.rent_amount
            if exchange_type
            not in (QuoteExchangeTypes.SHARE, QuoteExchangeTypes.DEPOSIT)
            else 0.0,
            deposit_amount=((product.rent_amount * 25) / 100)
            if exchange_type != QuoteExchangeTypes.SHARE
            else 0.0,
        )
        success, response = QuoteRepository.update_quote_type_remarks_history(
            new_quote, exchange_type, remarks
        )

        # Email to Owner
        email = product.user.email
        subject = "New Quote Placed"
        message = f"New Quote has been placed by {customer.full_name} for your product named {product.name}."
        success, response = send_email(
            subject=subject,
            message=message,
            receivers=[email],
        )
        LOGGER.info(
            "Quote Placed Email success and response: %s, %s", success, response
        )

        Notification.objects.create(
            user=product.user,
            text=f"New Quote has been placed by {customer.full_name} for your product named {product.name}.",
            type_id=new_quote.quote_id,
        )

        return (
            True,
            "Quote Placed successfully and confirmation mail has been sent to you..",
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_quote(
        quote_id,
        current_user,
        new_exchange_type,
        new_remarks,
        new_from_date,
        new_to_date,
        new_meetup_point,
    ):
        quote = get_or_none(Quote, quote_id=quote_id)
        if not quote:
            return False, ErrorMessages.INCORRECT_QUOTE_ID

        if quote.update_count == 5:
            return (
                False,
                "You cannot update this quote anymore, you can only accept or reject it.",
            )

        if new_exchange_type:
            quote.exchange_type = new_exchange_type
        if new_from_date:
            quote.from_date = datetime.strptime(new_from_date, "%d/%m/%Y")
        if new_to_date:
            quote.to_date = datetime.strptime(new_to_date, "%d/%m/%Y")
        if new_meetup_point:
            quote.meetup_point = new_meetup_point
        quote.remarks = new_remarks
        quote.last_updated_by = current_user
        quote.update_count = quote.update_count + 1
        quote.status = QuoteStatus.UPDATED
        quote.rent_amount = (
            quote.product.rent_amount
            if quote.exchange_type
            not in (QuoteExchangeTypes.SHARE, QuoteExchangeTypes.DEPOSIT)
            else 0.0
        )
        quote.deposit_amount = (
            ((quote.product.rent_amount * 25) / 100)
            if quote.exchange_type != QuoteExchangeTypes.SHARE
            else 0.0
        )
        quote.save()
        success, response = QuoteRepository.update_quote_type_remarks_history(
            quote, new_exchange_type, new_remarks
        )

        # send_email to another person in quote
        if current_user == quote.customer:
            user_to_be_notified = quote.owner
        elif current_user == quote.owner:
            user_to_be_notified = quote.customer
        # subject = "Your Quote has been updated."
        # message = f"Your Quote has been updated. \n Quote Type has been changed to {new_exchange_type} with remarks {new_remarks}. \n Please check and approve if everything looks good."
        # success, response = send_email(
        #     subject=subject,
        #     message=message,
        #     receivers=[user_to_be_notified.email],
        # )
        # LOGGER.info(
        #     "Quote Update Email success and response: %s, %s", success, response
        # )

        Notification.objects.create(
            user=user_to_be_notified,
            text=f"Your Quote has been updated. \n Quote Type has been changed to {new_exchange_type} with remarks {new_remarks}. \n Please check and approve if everything looks good.",
            type_id=quote_id,
        )
        return True, "Quote Updated Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def approve_quote(current_user, quote_id, new_remarks):
        quote = get_or_none(Quote, quote_id=quote_id)
        if not quote:
            return False, ErrorMessages.INCORRECT_QUOTE_ID
        if current_user == quote.customer:
            quote.approved_by_customer = True
            success, response = QuoteRepository.update_quote_type_remarks_history(
                quote, "APPROVED_BY_CUSTOMER", new_remarks
            )
        elif current_user == quote.owner:
            quote.approved_by_owner = True
            success, response = QuoteRepository.update_quote_type_remarks_history(
                quote, "APPROVED_BY_OWNER", new_remarks
            )
        quote.last_updated_by = current_user
        quote.remarks = new_remarks

        if quote.approved_by_customer and quote.approved_by_owner:
            quote.status = QuoteStatus.APPROVED
            quote.is_closed = True
            # TODO: Initialize payment
        else:
            # send_email to another person in quote
            if current_user == quote.customer:
                user_to_be_notified = quote.owner
            elif current_user == quote.owner:
                user_to_be_notified = quote.customer
            subject = "Quote has been Approved."
            message = f"Quote has been Approved by {current_user.full_name} for product named {quote.product.name}. Please login and check for more details."
            success, response = send_email(
                subject=subject,
                message=message,
                receivers=[user_to_be_notified.email],
            )
            LOGGER.info(
                "Quote Approved Email success and response: %s, %s", success, response
            )

            Notification.objects.create(
                user=user_to_be_notified,
                text=f"Quote has been Approved by {current_user.full_name} for product named {quote.product.name}.",
                type_id=quote_id,
            )

        quote.save()
        return True, "Quote Approved Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_quote_type_remarks_history(quote, new_type, new_remarks):
        quote_types_history = (
            literal_eval(quote.type_change_history) if quote.type_change_history else []
        )
        quote_types_history.append(new_type)
        quote.type_change_history = str(quote_types_history)

        quote_remarks_history = (
            literal_eval(quote.remarks_history) if quote.remarks_history else []
        )
        quote_remarks_history.append(new_remarks)
        quote.remarks_history = str(quote_remarks_history)
        quote.save()
        return True, "Quote History Updated Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def reject_quote(current_user, quote_id, new_remarks):
        quote = get_or_none(Quote, quote_id=quote_id)
        if not quote:
            return False, ErrorMessages.INCORRECT_QUOTE_ID
        if current_user == quote.customer:
            quote.rejected_by_customer = True
            success, response = QuoteRepository.update_quote_type_remarks_history(
                quote, "REJECTED_BY_CUSTOMER", new_remarks
            )
        elif current_user == quote.owner:
            quote.rejected_by_owner = True
            success, response = QuoteRepository.update_quote_type_remarks_history(
                quote, "REJECTED_BY_OWNER", new_remarks
            )
        quote.status = QuoteStatus.REJECTED
        quote.remarks = new_remarks
        quote.last_updated_by = current_user
        quote.is_closed = True
        quote.save()

        # Send email to another person in quote
        if current_user == quote.customer:
            user_to_be_notified = quote.owner
        elif current_user == quote.owner:
            user_to_be_notified = quote.customer
        subject = "Quote has been Rejected."
        message = f"Quote has been Rejected by {current_user.full_name} for product named {quote.product.name}. Please login and check for more details."
        success, response = send_email(
            subject=subject,
            message=message,
            receivers=[user_to_be_notified.email],
        )
        LOGGER.info(
            "Quote Rejected Email success and response: %s, %s", success, response
        )

        Notification.objects.create(
            user=user_to_be_notified,
            text=f"Quote has been Rejected by {current_user.full_name} for product named {quote.product.name}.",
            type_id=quote_id,
        )
        return True, "Quote Rejected Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_my_quotes(current_user):
        my_quotes = current_user.product_customer.all()
        if not my_quotes:
            return True, "No Quotes found from your side."
        quotes_data = QuoteSerializer(my_quotes, many=True).data
        return True, quotes_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_friends_quotes(current_user):
        friends_quotes = current_user.product_owner.all()
        if not friends_quotes:
            return True, "No Quotes placed for your products."
        quotes_data = QuoteSerializer(friends_quotes, many=True).data
        return True, quotes_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_quote_details(quote_id):
        quote = Quote.objects.filter(quote_id=quote_id).first()
        if not quote:
            return True, "Invalid Quote Id."
        quotes_data = QuoteSerializer(quote).data
        return True, quotes_data
