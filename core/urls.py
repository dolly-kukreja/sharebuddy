from django.urls import path
from core.views import (
    CustomUserController,
    OneTimePasswordController,
    AddressController,
    FriendRequestController,
    ProductController,
    FriendsController,
    NotificationController,
    QuoteController,
    PaymentLinkController,
    MessageController,
    WalletController,
    TransactionController,
)

urlpatterns = [
    # CustomUser URLs
    path("register", CustomUserController.register_user, name="register"),
    path("login", CustomUserController.login_user, name="login"),
    path(
        "update_user_details",
        CustomUserController.update_user_details,
        name="update_user_details",
    ),
    path(
        "get_user_details",
        CustomUserController.get_user_details,
        name="get_user_details",
    ),
    path(
        "get_user_profile",
        CustomUserController.get_user_profile,
        name="get_user_profile",
    ),
    path(
        "get_all_users",
        CustomUserController.get_all_users,
        name="get_all_users",
    ),
    path(
        "change_password",
        CustomUserController.change_password,
        name="change_password",
    ),
    path(
        "delete_user",
        CustomUserController.delete_user,
        name="delete_user",
    ),
    # OTP URLs
    path(
        "send_email_otp",
        OneTimePasswordController.send_email_otp,
        name="send_email_otp",
    ),
    path("send_sms_otp", OneTimePasswordController.send_sms_otp, name="send_sms_otp"),
    path(
        "verify_email_otp",
        OneTimePasswordController.verify_email_otp,
        name="verify_email_otp",
    ),
    path(
        "verify_sms_otp",
        OneTimePasswordController.verify_sms_otp,
        name="verify_sms_otp",
    ),
    # Address URLs
    path(
        "add_address",
        AddressController.add_address,
        name="add_address",
    ),
    path(
        "update_address",
        AddressController.update_address,
        name="update_address",
    ),
    path(
        "get_user_address",
        AddressController.get_user_address,
        name="get_user_address",
    ),
    # Product URLs
    path(
        "add_product",
        ProductController.add_product,
        name="add_product",
    ),
    path(
        "get_product_details",
        ProductController.get_product_details,
        name="get_product_details",
    ),
    path(
        "get_my_products",
        ProductController.get_my_products,
        name="get_my_products",
    ),
    path(
        "update_product",
        ProductController.update_product,
        name="update_product",
    ),
    path(
        "delete_product",
        ProductController.delete_product,
        name="delete_product",
    ),
    path(
        "shop_products",
        ProductController.shop_products,
        name="shop_products",
    ),
    path(
        "get_all_products",
        ProductController.get_all_products,
        name="get_all_products",
    ),
    # Friend Request URLs
    path(
        "send_friend_request",
        FriendRequestController.send_friend_request,
        name="send_friend_request",
    ),
    path(
        "action_on_friend_request",
        FriendRequestController.action_on_friend_request,
        name="action_on_friend_request",
    ),
    path(
        "get_friend_request",
        FriendRequestController.get_friend_request,
        name="get_friend_request",
    ),
    # Friend URLs
    path(
        "remove_friend",
        FriendsController.remove_friend,
        name="remove_friend",
    ),
    path(
        "get_friends",
        FriendsController.get_friends,
        name="get_friends",
    ),
    # Notification URLs
    path(
        "get_in_app_notifications",
        NotificationController.get_in_app_notifications,
        name="get_in_app_notifications",
    ),
    path(
        "mark_notification_as_read",
        NotificationController.mark_notification_as_read,
        name="mark_notification_as_read",
    ),
    # Quote URLs
    path(
        "place_quote",
        QuoteController.place_quote,
        name="place_quote",
    ),
    path(
        "update_quote",
        QuoteController.update_quote,
        name="update_quote",
    ),
    path(
        "approve_quote",
        QuoteController.approve_quote,
        name="approve_quote",
    ),
    path(
        "reject_quote",
        QuoteController.reject_quote,
        name="reject_quote",
    ),
    path(
        "get_my_quotes",
        QuoteController.get_my_quotes,
        name="get_my_quotes",
    ),
    path(
        "get_all_quotes",
        QuoteController.get_all_quotes,
        name="get_all_quotes",
    ),
    path(
        "get_friends_quotes",
        QuoteController.get_friends_quotes,
        name="get_friends_quotes",
    ),
    path(
        "get_quote_details",
        QuoteController.get_quote_details,
        name="get_quote_details",
    ),
    path(
        "update_exchange_status",
        QuoteController.update_exchange_status,
        name="update_exchange_status",
    ),
    path(
        "update_return_status",
        QuoteController.update_return_status,
        name="update_return_status",
    ),
    path(
        "update_user_ratings",
        QuoteController.update_user_ratings,
        name="update_user_ratings",
    ),
    path(
        "update_product_ratings",
        QuoteController.update_product_ratings,
        name="update_product_ratings",
    ),
    ## Payment URLs
    path(
        "payment_link_webhook",
        PaymentLinkController.payment_link_webhook,
        name="payment_link_webhook",
    ),
    ## Message URLs
    path(
        "message_list",
        MessageController.message_list,
        name="message_list",
    ),
    path(
        "get_last_message",
        MessageController.get_last_message,
        name="get_last_message",
    ),
    ## Wallet URLs
    path(
        "get_wallet_balance",
        WalletController.get_wallet_balance,
        name="get_wallet_balance",
    ),
    path(
        "debit_wallet_cash",
        WalletController.debit_wallet_cash,
        name="debit_wallet_cash",
    ),
    ## Transaction URLs
    path(
        "get_all_transactions",
        TransactionController.get_all_transactions,
        name="get_all_transactions",
    ),
    path(
        "get_my_transactions",
        TransactionController.get_my_transactions,
        name="get_my_transactions",
    ),
]
