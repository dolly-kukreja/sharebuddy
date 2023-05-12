import logging
from ast import literal_eval
from datetime import datetime

from django.db.models import QuerySet

from core.constants import (
    ErrorMessages,
    PaymentLinkTransactionTypes,
    QuoteExchangeTypes,
    QuoteStatus,
    TransactionSourceTarget,
    TransactionStatus,
    TransactionType,
)
from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_none
from core.models import CustomUser, Notification, Product, Quote, Transaction, Wallet
from core.repositories.paymentlink import PaymentLinkRepostitory
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
        message = f"New Quote has been placed by {customer.full_name} for your product named {product.name}. Please login and check for more details."
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
            quote.is_approved = True
            quote.save()
            success, response = QuoteRepository.handle_approved_quote_process(
                quote=quote
            )
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
        my_quotes = current_user.product_customer.all().order_by("-created_date")
        if not my_quotes:
            return True, "No Quotes found from your side."
        quotes_data = QuoteSerializer(my_quotes, many=True).data
        return True, quotes_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_all_quotes():
        all_quotes = Quote.objects.all().order_by("-created_date")
        if not all_quotes:
            return True, "No Quotes placed yet."
        quotes_data = QuoteSerializer(all_quotes, many=True).data
        return True, quotes_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_friends_quotes(current_user):
        friends_quotes = current_user.product_owner.all().order_by("-created_date")
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

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def calculate_average_ratings(ratings):
        multiplication_sum = 0
        for rating, ratings_by in ratings.items():
            multiplication_sum += int(rating) * ratings_by
        average_ratings = multiplication_sum / (sum(ratings.values()))
        return average_ratings

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_user_ratings(current_user, quote_id, ratings):
        ratings = int(ratings)
        quote = Quote.objects.filter(quote_id=quote_id).first()
        if not quote:
            return False, "Incorrect Quote ID."
        if current_user == quote.customer:
            user = quote.owner
            quote.owner_ratings = ratings
        if current_user == quote.owner:
            user = quote.customer
            quote.customer_ratings = ratings
        quote.save()
        existing_ratings = user.ratings
        if not existing_ratings:
            existing_ratings = {ratings: 1}
        elif existing_ratings.get(ratings):
            existing_ratings[ratings] += 1
        else:
            existing_ratings.update({ratings: 1})
        average_ratings = QuoteRepository.calculate_average_ratings(existing_ratings)
        user.ratings = existing_ratings
        user.average_ratings = average_ratings
        user.save()
        return True, "Ratings Updated Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_product_ratings(quote_id, ratings):
        ratings = int(ratings)
        quote = Quote.objects.filter(quote_id=quote_id).first()
        if not quote:
            return False, "Incorrect Quote ID."
        quote.product_ratings = ratings
        quote.save()
        product = quote.product
        existing_ratings = product.ratings
        if not existing_ratings:
            existing_ratings = {ratings: 1}
        elif existing_ratings.get(ratings):
            existing_ratings[ratings] += 1
        else:
            existing_ratings.update({ratings: 1})
        average_ratings = QuoteRepository.calculate_average_ratings(existing_ratings)
        product.ratings = existing_ratings
        product.average_ratings = average_ratings
        product.save()
        return True, "Ratings Updated Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def handle_approved_quote_process(quote):
        if quote.exchange_type == QuoteExchangeTypes.SHARE:
            subject = "Quote has been approved."
            message_for_customer = f"Congratulations!!! \n Your Quote has been Approved for product named {quote.product.name}. As per your quote, you guys have decided to meet at {quote.meetup_point}. We request you to meet at decided meetup point and update about the same on our website, so that we can process your quote further. If you fail to update your quote before your start_date, we'll have to unfortunately close your quote and then no payment will be credited or debited. Hence, Please share the latest updates with us. We appreciate your time and understanding. \n Thankyou"
            message_for_owner = f"Quote has been Approved for your product named {quote.product.name}. As per your quote, you guys have decided to meet at {quote.meetup_point}. We request you to meet at decided meetup point and update about the same on our website, so that we can process your quote further. If you fail to update the quote before your start_date, we'll have to unfortunately close your quote and then no payment will be credited or debited. Hence, Please share the latest updates with us. We appreciate your time and understanding. \n Thankyou"
            success, response = send_email(
                subject=subject,
                message=message_for_customer,
                receivers=[quote.customer.email],
            )
            LOGGER.info(
                "Quote Approved Email success and response: %s, %s", success, response
            )
            success, response = send_email(
                subject=subject,
                message=message_for_owner,
                receivers=[quote.owner.email],
            )
            LOGGER.info(
                "Quote Approved Email success and response: %s, %s", success, response
            )
        elif quote.exchange_type == QuoteExchangeTypes.DEPOSIT:
            subject = "Quote has been approved."
            message_for_customer = f"Congratulations!!! \n Your Quote has been Approved for product named {quote.product.name}. As per your quote, you guys has decided to go with the Deposit exchange type. So, you will get the payment link soon over the mail, please make the payment and then we'll proceed your quote fruther for sharing. If you fail to update the quote before your start_date, we'll have to unfortunately close your quote and then no payment will be credited or debited. We appreciate your time and understanding. \n Thankyou"
            message_for_owner = f"Quote has been Approved for your product named {quote.product.name}. As per your quote, you guys has decided to go with the Depos``it exchange type. Hence, We have shared the payment link with the customer for Payment and will update you the same once customer has made the payment. But you'll get your payment once product is shared, until then your payment is safe with us. And once customer has made the payment, you can share your product with the customer. We appreciate your time and understanding. \n Thankyou"
            success, response = send_email(
                subject=subject,
                message=message_for_customer,
                receivers=[quote.customer.email],
            )
            LOGGER.info(
                "Quote Approved Email success and response: %s, %s", success, response
            )
            success, response = send_email(
                subject=subject,
                message=message_for_owner,
                receivers=[quote.owner.email],
            )
            LOGGER.info(
                "Quote Approved Email success and response: %s, %s", success, response
            )
            success, response = PaymentLinkRepostitory.send_payment_link(
                payment_type=PaymentLinkTransactionTypes.DEPOSIT,
                quote=quote,
                user=quote.customer,
            )
            LOGGER.info(
                "Payment Link Creation success and response: %s, %s", success, response
            )
        elif quote.exchange_type == QuoteExchangeTypes.RENT:
            subject = "Quote has been approved."
            message_for_customer = f"Congratulations!!! \n Your Quote has been Approved for product named {quote.product.name}. As per your quote, you guys has decided to go with the Rent exchange type. So, you will get the payment link soon over the mail, please make the payment and then we'll proceed your quote fruther for sharing. If you fail to update the quote before your start_date, we'll have to unfortunately close your quote and then no payment will be credited or debited. We appreciate your time and understanding. \n Thankyou"
            message_for_owner = f"Quote has been Approved for your product named {quote.product.name}. As per your quote, you guys has decided to go with the Rent exchange type. Hence, We have shared the payment link with the customer for Payment and will update you the same once customer has made the payment. And once customer has made the payment, you can share your product with the customer. We appreciate your time and understanding. \n Thankyou"
            success, response = send_email(
                subject=subject,
                message=message_for_customer,
                receivers=[quote.customer.email],
            )
            LOGGER.info(
                "Quote Approved Email success and response: %s, %s", success, response
            )
            success, response = send_email(
                subject=subject,
                message=message_for_owner,
                receivers=[quote.owner.email],
            )
            LOGGER.info(
                "Quote Approved Email success and response: %s, %s", success, response
            )
            success, response = PaymentLinkRepostitory.send_payment_link(
                payment_type=PaymentLinkTransactionTypes.RENT,
                quote=quote,
                user=quote.customer,
            )
            LOGGER.info(
                "Payment Link Creation success and response: %s, %s", success, response
            )
        quote.status = QuoteStatus.IN_TRANSIT
        quote.save()
        return True, "Emails Sent Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def after_payment_process(payment_link_object):
        quote = payment_link_object.quote
        admin_wallet = Wallet.objects.get(user__email="masters@gmail.com")
        admin_wallet.available_balance += payment_link_object.payment_amount
        admin_wallet.save()
        transaction = Transaction.objects.get(remarks=payment_link_object.link_id)
        transaction.status = TransactionStatus.COMPLETED
        transaction.save()
        if quote.exchange_type == QuoteExchangeTypes.RENT:
            quote.is_rent_paid = True
            quote.is_deposit_paid = True
            quote.last_updated_by = quote.customer
        if quote.exchange_type == QuoteExchangeTypes.DEPOSIT:
            quote.is_deposit_paid = True
            quote.last_updated_by = quote.customer
        quote.save()
        subject = "Recieved Payment."
        message_for_customer = f"We received your payment for {quote.product.name} and has informed the same to owner, so now you guys can exchange the product at the decided meet-up point. Once Exchanged, please update the same on the webiste, so that we can process your quote further. If you fail to update your quote before your start_date, we'll have to unfortunately close your quote and then no payment will be credited or debited. Hence, Please share the latest updates with us. We appreciate your time and understanding. \n Thankyou"
        message_for_owner = f"We have received the payment from customer for your product named {quote.product.name}. So, now you guys can exchange the product at the decided meet-up point. Once Exchanged, please update the same on the webiste, so that we can process your quote further.  And you'll get your payment once product is shared, until then your payment is safe with us. If you fail to update your quote before your start_date, we'll have to unfortunately close your quote and then no payment will be credited or debited. Hence, Please share the latest updates with us. We appreciate your time and understanding. \n Thankyou"
        success, response = send_email(
            subject=subject,
            message=message_for_customer,
            receivers=[quote.customer.email],
        )
        LOGGER.info(
            "Payment Done Email success and response: %s, %s", success, response
        )
        success, response = send_email(
            subject=subject,
            message=message_for_owner,
            receivers=[quote.owner.email],
        )
        LOGGER.info(
            "Payment Done Email success and response: %s, %s", success, response
        )
        return True, "Details Updated Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def close_quote_with_failed_payment(payment_link_object):
        quote = payment_link_object.quote
        quote.is_closed = True
        quote.last_updated_by = quote.customer
        quote.save()
        transaction = Transaction.objects.get(remarks=payment_link_object.link_id)
        transaction.status = TransactionStatus.FAILED
        transaction.save()
        subject = "Closing Quote due to Failed Payment."
        message_for_customer = f"Payment Link expired and you failed to make the payment for product named {quote.product.name}, hence closing the quote here only. \n Thankyou"
        message_for_owner = f"Customer failed to make the payment for your product named {quote.product.name}, hence closing the quote here only. \n Thankyou"
        success, response = send_email(
            subject=subject,
            message=message_for_customer,
            receivers=[quote.customer.email],
        )
        LOGGER.info(
            "Quote Closed Email success and response: %s, %s", success, response
        )
        success, response = send_email(
            subject=subject,
            message=message_for_owner,
            receivers=[quote.owner.email],
        )
        LOGGER.info(
            "Quote Closed Email success and response: %s, %s", success, response
        )
        return True, "Details Updated Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_exchange_status(current_user, quote_id):
        quote = Quote.objects.filter(quote_id=quote_id).first()
        if not quote:
            return True, "Invalid Quote Id."
        if current_user == quote.customer:
            quote.exchanged_by_customer = True
        if current_user == quote.owner:
            quote.exchanged_by_owner = True
        quote.last_updated_by = current_user
        if quote.exchanged_by_owner and quote.exchanged_by_customer:
            quote.is_exchanged = True
            if quote.exchange_type == QuoteExchangeTypes.RENT:
                payment_amount = quote.rent_amount
                admin_user = CustomUser.objects.filter(
                    email="masters@gmail.com"
                ).first()
                admin_wallet = Wallet.objects.get(user=admin_user)
                admin_wallet.available_balance -= payment_amount
                admin_wallet.save()
                owner_wallet = Wallet.objects.get(user=quote.owner)
                owner_wallet.available_balance += payment_amount
                owner_wallet.save()
                Transaction.objects.create(
                    from_user=admin_user,
                    to_user=quote.owner,
                    quote=quote,
                    amount=payment_amount,
                    ttype=TransactionType.DEBIT,
                    status=TransactionStatus.COMPLETED,
                    source=TransactionSourceTarget.WALLET,
                    target=TransactionSourceTarget.WALLET,
                )
            subject = "Product has been exchanged."
            message_for_owner = f"Your Product named {quote.product.name} has been exchanged. We have credited your payment, please check you wallet for the same. And do update your details once you receive back your product, so that we can close your quote. We appreciate your time and understanding. \n Thankyou"
            message_for_customer = f"You have received the Product named {quote.product.name}. Please do update your details once you return back the product, so that we can close your quote and disburse your payment. We appreciate your time and understanding. \n Thankyou"
            success, response = send_email(
                subject=subject,
                message=message_for_customer,
                receivers=[quote.customer],
            )
            LOGGER.info(
                "Product Exchanged Email success and response: %s, %s",
                success,
                response,
            )
            success, response = send_email(
                subject=subject,
                message=message_for_owner,
                receivers=[quote.owner],
            )
            LOGGER.info(
                "Product Exchanged Email success and response: %s, %s",
                success,
                response,
            )
        quote.save()
        return True, "Product Exchanged Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_return_status(current_user, quote_id):
        quote = Quote.objects.filter(quote_id=quote_id).first()
        if not quote:
            return True, "Invalid Quote Id."
        if current_user == quote.customer:
            quote.returned_by_customer = True
        if current_user == quote.owner:
            quote.returned_by_owner = True
        quote.last_updated_by = current_user
        if quote.returned_by_customer and quote.returned_by_owner:
            quote.is_closed = True
            if quote.exchange_type in (
                QuoteExchangeTypes.RENT,
                QuoteExchangeTypes.DEPOSIT,
            ):
                payment_amount = quote.deposit_amount
                admin_user = CustomUser.objects.filter(
                    email="masters@gmail.com"
                ).first()
                admin_wallet = Wallet.objects.get(user=admin_user)
                admin_wallet.available_balance -= payment_amount
                admin_wallet.save()
                customer_wallet = Wallet.objects.get(user=quote.customer)
                customer_wallet.available_balance += payment_amount
                customer_wallet.save()
                Transaction.objects.create(
                    from_user=admin_user,
                    to_user=quote.customer,
                    quote=quote,
                    amount=payment_amount,
                    ttype=TransactionType.DEBIT,
                    status=TransactionStatus.COMPLETED,
                    source=TransactionSourceTarget.WALLET,
                    target=TransactionSourceTarget.WALLET,
                )
            subject = "Product has been returned."
            message_for_owner = f"Your Product named {quote.product.name} has been returned. We are closing this quote here. We appreciate your time and understanding. \n Thankyou"
            message_for_customer = f"You returned the Product named {quote.product.name}. We have credited your deposit amount, please check your wallet. We appreciate your time and understanding. \n Thankyou"
            success, response = send_email(
                subject=subject,
                message=message_for_customer,
                receivers=[quote.customer],
            )
            LOGGER.info(
                "Quote Closed Email success and response: %s, %s", success, response
            )
            success, response = send_email(
                subject=subject,
                message=message_for_owner,
                receivers=[quote.owner],
            )
            LOGGER.info(
                "Quote Closed Email success and response: %s, %s", success, response
            )
        quote.save()
        return True, "Quote Closed Successfully."
