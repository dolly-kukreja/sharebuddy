from django.shortcuts import render

# Create your views here.

from core.controllers.customuser import CustomUserController
from core.controllers.otp import OneTimePasswordController
from core.controllers.address import AddressController
from core.controllers.friendrequest import FriendRequestController
from core.controllers.product import ProductController
from core.controllers.friends import FriendsController
from core.controllers.notification import NotificationController
from core.controllers.quote import QuoteController
from core.controllers.paymentlink import PaymentLinkController
from core.controllers.message import MessageController
from core.controllers.wallet import WalletController
from core.controllers.transaction import TransactionController
