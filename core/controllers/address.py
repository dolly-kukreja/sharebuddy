from rest_framework.decorators import api_view
from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.repositories.address import AddressRepository
from django.contrib.auth.decorators import login_required


class AddressController:
    @staticmethod
    @api_view(["POST"])
    @login_required
    def add_address(request):
        user = request.user
        post_data = request.data
        line1 = post_data.get("line1")
        line2 = post_data.get("line2")
        city = post_data.get("city")
        state = post_data.get("state")
        country = post_data.get("country")
        landmark = post_data.get("landmark")
        pincode = post_data.get("pincode")
        if (
            not line1
            or not line2
            or not city
            or not state
            or not country
            or not landmark
            or not pincode
        ):
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = AddressRepository.add_user_address(
            user=user,
            line1=line1,
            line2=line2,
            city=city,
            state=state,
            country=country,
            landmark=landmark,
            pincode=pincode,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    def update_address(request):
        user = request.user
        post_data = request.data
        line1 = post_data.get("line1")
        line2 = post_data.get("line2")
        city = post_data.get("city")
        state = post_data.get("state")
        country = post_data.get("country")
        landmark = post_data.get("landmark")
        pincode = post_data.get("pincode")
        success, response = AddressRepository.update_user_address(
            user=user,
            line1=line1,
            line2=line2,
            city=city,
            state=state,
            country=country,
            landmark=landmark,
            pincode=pincode,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    def get_user_address(request):
        user = request.user
        success, response = AddressRepository.get_user_address(user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
