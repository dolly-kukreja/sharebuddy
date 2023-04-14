from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

from core.constants import ProductCategories
from core.helpers.base import BadRequestJSONResponse, SuccessJSONResponse
from core.helpers.decorators import validate_user_details
from core.models import Product
from core.repositories.product import ProductRepository
from core.serializers.root_serializers import ProductSerializer


class ProductController:
    @staticmethod
    @api_view(["POST"])
    @login_required
    @validate_user_details()
    def add_product(request):
        user = request.user
        post_data = request.data
        category = post_data.get("category", ProductCategories.CLOTH)
        name = post_data.get("name")
        description = post_data.get("description")
        product_photo = post_data.get("photo")
        rent_amount = post_data.get("rent_amount")
        if (
            not name
            or not description
            or not product_photo
            or not rent_amount
            or not category
        ):
            return BadRequestJSONResponse(message="Invalid Params")
        success, response = ProductRepository.add_product(
            user=user,
            name=name,
            description=description,
            product_photo=product_photo,
            category=category,
            rent_amount=rent_amount,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse("Product Added Successfully.")

    @staticmethod
    @api_view(["GET"])
    @login_required
    @validate_user_details()
    def get_product_details(request):
        request_params = request.GET
        product_id = request_params.get("product_id")
        if not product_id:
            return BadRequestJSONResponse(message="Product Id is required.")
        product = Product.objects.filter(product_id=product_id).first()
        if not product:
            return BadRequestJSONResponse(message="Invalid Product Id.")
        return SuccessJSONResponse(ProductSerializer(product).data)

    @staticmethod
    @api_view(["GET"])
    @login_required
    @validate_user_details()
    def get_all_products(request):
        user = request.user
        success, response = ProductRepository.get_all_products(user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    @validate_user_details()
    def update_product(request):
        post_data = request.data
        product_id = post_data.get("product_id")
        category = post_data.get("category")
        name = post_data.get("name")
        description = post_data.get("description")
        product_photo = post_data.get("product_photo")
        rent_amount = post_data.get("rent_amount")
        is_available = post_data.get("is_available")
        if not product_id:
            return BadRequestJSONResponse("Product ID is required.")
        success, response = ProductRepository.update_product_details(
            product_id=product_id,
            category=category,
            name=name,
            description=description,
            product_photo=product_photo,
            rent_amount=rent_amount,
            is_available=is_available,
        )
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["POST"])
    @login_required
    @validate_user_details()
    def delete_product(request):
        product_id = request.data.get("product_id")
        if not product_id:
            return BadRequestJSONResponse("Invalid Params.")
        success, response = ProductRepository.delete_product(product_id)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)

    @staticmethod
    @api_view(["GET"])
    @login_required
    @validate_user_details()
    def shop_products(request):
        user = request.user
        success, response = ProductRepository.shop_products(user)
        if not success:
            return BadRequestJSONResponse(message=response)
        return SuccessJSONResponse(response)
