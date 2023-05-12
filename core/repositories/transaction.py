import logging

from django.db.models import Q, QuerySet

from core.helpers.decorators import handle_unknown_exception
from core.models import Transaction
from core.serializers.root_serializers import TransactionSerializer

LOGGER = logging.getLogger(__name__)


class TransactionRepository:
    def __init__(
        self,
        *args,
        item: Transaction = None,
        many: bool = False,
        item_list: QuerySet = None,
        **kwargs,
    ):
        super(TransactionRepository, self).__init__(
            *args,
            model=Transaction,
            item=item,
            many=many,
            item_list=item_list,
            **kwargs,
        )

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_all_transactions():
        transactions = Transaction.objects.all().order_by("-created_date")
        transactions_data = TransactionSerializer(transactions, many=True).data
        return True, transactions_data

    @staticmethod
    @handle_unknown_exception(logger=LOGGER)
    def get_my_transactions(user):
        transactions = Transaction.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        ).order_by("-created_date")
        transactions_data = TransactionSerializer(transactions, many=True).data
        return True, transactions_data
