from ast import literal_eval
import logging

from django.core.files import File
from django.db.models import QuerySet
from core.constants import NotificationType

from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_none
from core.models import CustomUser, Friends, Notification, Product
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
        rent_amount,
    ):
        try:
            new_product = Product.objects.create(
                user=user,
                category=category,
                name=name,
                description=description,
                photo=product_photo,
                rent_amount=rent_amount,
                is_available=True,
                is_active=True,
            )
            new_product.save()
            success, response = ProductRepository.notify_all_friends(new_product, "add")
            return True, "Product Added successfully."
        except Exception as ex:
            return False, str(ex)

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_my_products(user):
        products = Product.objects.filter(user=user, is_active=True).order_by(
            "-created_date"
        )
        if not products:
            return True, "No Products Found."
        products_serialized_data = ProductSerializer(products, many=True).data
        return True, products_serialized_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_product_details(
        product_id,
        category,
        name,
        description,
        product_photo,
        rent_amount,
        is_available,
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

        if rent_amount:
            product.rent_amount = rent_amount

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
        success, response = ProductRepository.notify_all_friends(product, "delete")
        return True, "Product Deleted Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def shop_products(current_user):
        friend_object = Friends.objects.filter(user=current_user).first()
        if not friend_object:
            return True, "No Friends Added to Shop."
        products_queryset = Product.objects.none()
        for user_id in literal_eval(friend_object.friends_list):
            user = CustomUser.objects.get(user_id=user_id)
            user_products = user.user_product.filter(is_available=True, is_active=True)
            products_queryset = products_queryset | user_products
        if not products_queryset:
            return True, "No Products to Shop."
        products_queryset = products_queryset.order_by("-created_date")
        products_data = ProductSerializer(products_queryset, many=True).data
        return True, products_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_all_products():
        all_products = Product.objects.filter(is_active=True).order_by("-created_date")
        products_data = ProductSerializer(all_products, many=True).data
        return True, products_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def notify_all_friends(product, action):
        friend_object = Friends.objects.filter(user=product.user).first()
        if not friend_object:
            return True, "No Friends to Notify."
        friends_id_list = literal_eval(friend_object.friends_list)
        friends = CustomUser.objects.filter(user_id__in=friends_id_list)
        for friend in friends:
            Notification.objects.create(
                user=friend,
                text=f"Product has been {action}ed by your friend {product.user.full_name}.",
                type=NotificationType.PRODUCT,
                type_id=product.product_id,
            )
        return True, "Notification Sent"
