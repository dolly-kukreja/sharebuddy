import logging

from django.core.files import File
from django.db.models import QuerySet

from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_none
from core.models import CustomUser, Product
from core.serializers.root_serializers import ProductSerializer

LOGGER = logging.getLogger(__name__)


class ProductRepository:
    def __init__(
        self,
        *args,
        item: Product = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(ProductRepository, self).__init__(
            *args, model=Product, item=item, many=many, item_list=item_list, **kwargs
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def add_product(
        user: CustomUser,
        name: str,
        description: str,
        product_photo: File,
        category: str,
        price,
    ):
        try:
            new_product = Product.objects.create(
                user=user,
                category=category,
                name=name,
                description=description,
                photo=product_photo,
                price=price,
                is_available=True,
                is_active=True,
            )
            new_product.save()
            return True, "Product Added successfully."
        except Exception as ex:
            return False, str(ex)

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_all_products(user):
        products = Product.objects.filter(user=user, is_active=True)
        if not products:
            return False, "No Products Found."
        products_serialized_data = ProductSerializer(products, many=True).data
        return True, products_serialized_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_product_details(
        product_id, category, name, description, product_photo, price, is_available
    ):
        product = get_or_none(Product, product_id=product_id)
        if not product:
            return False, "Invalid Product ID."

        if category:
            product.category = category

        if name:
            product.name = name

        if description:
            product.description = description

        if product_photo:
            product.photo = product_photo

        if price:
            product.price = price

        if is_available is not None:
            product.is_available = is_available
        product.save()
        return True, "Product Details Updated Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def delete_product(product_id):
        product = get_or_none(Product, product_id=product_id)
        if not product:
            return False, "Invalid Product ID."
        product.is_available = False
        product.is_active = False
        product.save()
        return True, "Product Deleted Successfully."
