class ProductCategories:
    CLOTH = "CLOTH"
    ELECTRONIC = "ELECTRONIC"
    FOOTWEAR = "FOOTWEAR"
    ACCESSORIES = "ACCESSORIES"
    STATIONARY = "STATIONARY"


class ProductSharingTypes:
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
