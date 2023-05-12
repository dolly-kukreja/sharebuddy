from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import api_view

from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.quote import QuoteRepository


class QuoteController:
    @staticmethod
    @api_view(["POST"])
    @login_required
    def place_quote(request):
        customer = request.user
        product_id = request.POST.get("product_id")
        exchange_type = request.POST.get("exchange_type")
        remarks = request.POST.get("remarks")
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        meetup_point = request.POST.get("meetup_point")
        if (
            not product_id
            or not exchange_type
            or not remarks
            or not from_date
            or not to_date
            or not meetup_point
        ):
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = QuoteRepository.place_quote(
            product_id=product_id,
            customer=customer,
            exchange_type=exchange_type,
            from_date=from_date,
            to_date=to_date,
            meetup_point=meetup_point,
            remarks=remarks,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def update_quote(request):
        current_user = request.user
        quote_id = request.POST.get("quote_id")
        new_exchange_type = request.POST.get("exchange_type")
        new_remarks = request.POST.get("remarks")
        new_from_date = request.POST.get("from_date")
        new_to_date = request.POST.get("to_date")
        new_meetup_point = request.POST.get("meetup_point")
        if not quote_id or not new_remarks:
            return BadRequestJSONResponse("Invalid Params")
        success, response = QuoteRepository.update_quote(
            quote_id=quote_id,
            current_user=current_user,
            new_exchange_type=new_exchange_type,
            new_from_date=new_from_date,
            new_to_date=new_to_date,
            new_meetup_point=new_meetup_point,
            new_remarks=new_remarks,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def approve_quote(request):
        current_user = request.user
        quote_id = request.POST.get("quote_id")
        new_remarks = request.POST.get("remarks")
        if not quote_id or not new_remarks:
            return BadRequestJSONResponse("Invalid Params")
        success, response = QuoteRepository.approve_quote(
            current_user=current_user,
            quote_id=quote_id,
            new_remarks=new_remarks,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def reject_quote(request):
        current_user = request.user
        quote_id = request.POST.get("quote_id")
        new_remarks = request.POST.get("remarks")
        if not quote_id or not new_remarks:
            return BadRequestJSONResponse("Invalid Params")
        success, response = QuoteRepository.reject_quote(
            current_user=current_user,
            quote_id=quote_id,
            new_remarks=new_remarks,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_my_quotes(request):
        success, response = QuoteRepository.get_my_quotes(current_user=request.user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    @user_passes_test(lambda u: u.is_superuser)
    def get_all_quotes(request):
        success, response = QuoteRepository.get_all_quotes()
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_friends_quotes(request):
        success, response = QuoteRepository.get_friends_quotes(
            current_user=request.user
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_quote_details(request):
        quote_id = request.GET.get("quote_id")
        if not quote_id:
            return BadRequestJSONResponse("Invalid Params")
        success, response = QuoteRepository.get_quote_details(quote_id=quote_id)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def update_exchange_status(request):
        current_user = request.user
        quote_id = request.POST.get("quote_id")
        if not quote_id:
            return BadRequestJSONResponse("Invalid Params")
        success, response = QuoteRepository.update_exchange_status(
            current_user=current_user,
            quote_id=quote_id,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def update_return_status(request):
        current_user = request.user
        quote_id = request.POST.get("quote_id")
        if not quote_id:
            return BadRequestJSONResponse("Invalid Params")
        success, response = QuoteRepository.update_return_status(
            current_user=current_user,
            quote_id=quote_id,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def update_user_ratings(request):
        current_user = request.user
        quote_id = request.POST.get("quote_id")
        ratings = request.POST.get("ratings")
        if not quote_id or not ratings:
            return BadRequestJSONResponse("Invalid Params")
        success, response = QuoteRepository.update_user_ratings(
            current_user=current_user,
            quote_id=quote_id,
            ratings=ratings,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def update_product_ratings(request):
        quote_id = request.POST.get("quote_id")
        ratings = request.POST.get("ratings")
        if not quote_id or not ratings:
            return BadRequestJSONResponse("Invalid Params")
        success, response = QuoteRepository.update_product_ratings(
            quote_id=quote_id,
            ratings=ratings,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
