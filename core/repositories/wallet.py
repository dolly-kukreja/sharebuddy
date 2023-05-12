import logging

from django.db.models import QuerySet

from core.constants import TransactionSourceTarget, TransactionStatus, TransactionType
from core.helpers.decorators import handle_unknown_exception
from core.models import Transaction, Wallet

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

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def debit_wallet_cash(user, amount):
        user_wallet = Wallet.objects.get(user=user)
        user_wallet.available_balance -= amount
        user_wallet.save()
        Transaction.objects.create(
            from_user=user,
            to_user=user,
            amount=amount,
            status=TransactionStatus.COMPLETED,
            ttype=TransactionType.DEBIT,
            source=TransactionSourceTarget.WALLET,
            target=TransactionSourceTarget.BANK,
        )
        return True, "Wallet Cash Transferred Successfully."
