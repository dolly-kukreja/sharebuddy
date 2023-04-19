import logging
from django.db.models import QuerySet
from core.helpers.decorators import handle_unknown_exception
from core.models import Wallet

LOGGER = logging.getLogger(__name__)


class WalletRepository:
    def __init__(
        self,
        *args,
        item: Wallet = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(WalletRepository, self).__init__(
            *args,
            model=Wallet,
            item=item,
            many=many,
            item_list=item_list,
            **kwargs,
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_wallet_balance(user):
        wallet = Wallet.objects.get(user=user)
        return True, wallet.available_balance
