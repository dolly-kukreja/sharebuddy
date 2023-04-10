import logging

from django.db.models import QuerySet

from core.helpers.decorators import handle_unknown_exception
from core.helpers.query_search import get_or_create
from core.models import Address
from core.serializers.root_serializers import AddressSerializer

LOGGER = logging.getLogger(__name__)


class AddressRepository:
    def __init__(
        self,
        *args,
        item: Address = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(AddressRepository, self).__init__(
            *args, model=Address, item=item, many=many, item_list=item_list, **kwargs
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def add_user_address(user, line1, line2, city, state, country, landmark, pincode):
        address_object = get_or_create(Address, user=user)
        address_object.line1 = line1
        address_object.line2 = line2
        address_object.city = city
        address_object.state = state
        address_object.country = country
        address_object.landmark = landmark
        address_object.pincode = pincode
        address_object.save()
        return True, "Address Added Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def update_user_address(
        user, line1, line2, city, state, country, landmark, pincode
    ):
        address_object = get_or_create(Address, user=user)
        if line1:
            address_object.line1 = line1
        if line2:
            address_object.line2 = line2
        if city:
            address_object.city = city
        if state:
            address_object.state = state
        if country:
            address_object.country = country
        if landmark:
            address_object.landmark = landmark
        if pincode:
            address_object.pincode = pincode
        address_object.save()
        return True, "Address Updated Successfully."

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_user_address(user):
        user_address = user.address_user.all()
        if not user_address:
            return False, "No Address Found"
        address_data = AddressSerializer(user_address.first()).data
        return True, address_data
