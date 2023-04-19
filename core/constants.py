class ProductCategories:
    CLOTH = "CLOTH"
    ELECTRONIC = "ELECTRONIC"
    FOOTWEAR = "FOOTWEAR"
    ACCESSORIES = "ACCESSORIES"
    STATIONARY = "STATIONARY"


class QuoteExchangeTypes:
    SHARE = "SHARE"
    RENT = "RENT"
    DEPOSIT = "DEPOSIT"


class RequestContentTypes:
    APPLICATION_JSON = "application/json"


EMAIL_SENDER = "sharebuddy3@gmail.com"


class OTPKeyNameTypes:
    EMAIL = 1
    MOBILE = 2


class FriendRequestStatus:
    PENDING = 1
    ACCEPT = 2
    REJECT = 3
    REMOVE = 4


class QuoteStatus:
    PLACED = 1
    UPDATED = 2
    APPROVED = 3
    REJECTED = 4
    IN_TRANSIT = 5
    SHARED = 6
    COMPLETED = 7


class ErrorMessages:
    INCORRECT_QUOTE_ID = "Incorrect Quote ID."


class NotificationStatus:
    READ = "READ"
    UNREAD = "UNREAD"


class NotificationChannel:
    IN_APP = "IN_APP"
    MOBILE = "MOBILE"
    EMAIL = "EMAIL"


class NotificationType:
    PRODUCT = "PRODUCT"
    FRIEND_REQUEST = "FRIEND_REQUEST"
    FRIEND = "FRIEND"
    QUOTE = "QUOTE"


class PaymentLinkStatus:
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    EXPIRED = "EXPIRED"


class PaymentLinkTransactionTypes:
    RENT = "RENT"
    DEPOSIT = "DEPOSIT"


class TransactionType:
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class TransactionSourceTarget:
    WALLET = "WALLET"
    BANK = "BANK"
