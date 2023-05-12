import re
import random
from django.db import models
from django.db.models import (
    Model,
    IntegerField,
    CharField,
    BooleanField,
    EmailField,
    ImageField,
    DateField,
    ForeignKey,
    DateTimeField,
    DecimalField,
    TextField,
    JSONField,
)
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from datetime import datetime
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from core.constants import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
    OTPKeyNameTypes,
    FriendRequestStatus,
    PaymentLinkStatus,
    ProductCategories,
    QuoteExchangeTypes,
    QuoteStatus,
    TransactionType,
    TransactionSourceTarget,
    TransactionStatus,
)

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password,
        first_name=None,
        last_name=None,
        mobile_number=None,
        is_mobile_number_verified=False,
    ):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=mobile_number,
            is_mobile_number_verified=is_mobile_number_verified,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile_number, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """

        if not re.search(r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$", email):
            raise ValueError("Invalid email address")
        user = self.create_user(email, mobile_number=mobile_number, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def generate_unique_id():
    unique_id = "".join(
        [random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVXYZ") for i in range(10)]
    )
    return unique_id


def get_profile_photo_filepath_with_name(instance, name):
    date = datetime.strftime(datetime.now(), "%Y_%m_%d_%H_%M_%S")
    ext = name.split(".")[-1]
    return "profile_photo/" + date + instance.user_id + "." + ext


def get_product_photo_filepath_with_name(instance, name):
    date = datetime.strftime(datetime.now(), "%Y_%m_%d_%H_%M_%S")
    ext = name.split(".")[-1]
    return "product_photo/" + date + instance.product_id + "." + ext


# CUSTOM USER


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = CharField(
        max_length=255,
        editable=False,
        default=generate_unique_id,
        unique=True,
        null=True,
    )
    first_name = CharField(max_length=700, null=True, blank=True)
    last_name = CharField(max_length=700, null=True, blank=True)
    mobile_number = CharField(max_length=15, editable=True, null=True)
    is_mobile_number_verified = BooleanField(default=False)
    email = EmailField(verbose_name="email address", max_length=255, unique=True)
    is_email_verified = BooleanField(default=False)
    dob = DateField(null=True)
    profile_photo = ImageField(
        null=True, blank=True, upload_to=get_profile_photo_filepath_with_name
    )
    is_active = BooleanField(default=True, verbose_name="Active")
    is_staff = BooleanField(default=False, verbose_name="Staff")
    is_superuser = BooleanField(default=False, verbose_name="SuperUser")
    average_ratings = IntegerField(default=0)
    ratings = JSONField(null=True, blank=True)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELD = ["email"]
    objects = CustomUserManager()

    @property
    def full_name(self):
        full_name = self.first_name
        if self.last_name:
            full_name = f"{full_name} {self.last_name}"
        return full_name

    def __str__(
        self,
    ):
        return str(self.email)


class Address(Model):
    user = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="address_user")
    line1 = CharField(max_length=300)
    line2 = CharField(max_length=300, null=True, blank=True)
    city = CharField(max_length=200, default="MUMBAI")
    state = CharField(max_length=200, default="MAHARASHTRA")
    country = CharField(max_length=200, default="INDIA")
    landmark = CharField(max_length=100, null=True, blank=True)
    pincode = CharField(max_length=6, null=True, blank=True)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(
        self,
    ):
        return str(self.user.email) + "-" + self.city


class OneTimePassword(Model):
    key_name_choices = (
        (OTPKeyNameTypes.MOBILE, "MOBILE"),
        (OTPKeyNameTypes.EMAIL, "EMAIL"),
    )
    # purpose_choices = (
    #     (OTPPurposeTypes.EMAIL_VERIFICATION, OTPPurposeTypes.EMAIL_VERIFICATION),
    #     (
    #         OTPPurposeTypes.MOBILE_NUMBER_VERIFICATION,
    #         OTPPurposeTypes.MOBILE_NUMBER_VERIFICATION,
    #     ),
    #     (OTPPurposeTypes.BUY_CONFIMATION, OTPPurposeTypes.BUY_CONFIMATION),
    #     (OTPPurposeTypes.SELL_CONFIRMATION, OTPPurposeTypes.SELL_CONFIRMATION),
    #     (OTPPurposeTypes.PASSWORD_RESET, OTPPurposeTypes.PASSWORD_RESET),
    #     (OTPPurposeTypes.LOGIN, OTPPurposeTypes.LOGIN),
    # )
    key_name = CharField(max_length=15, choices=key_name_choices)
    key_value = CharField(max_length=256)  # Email or Mobile Number
    password = CharField(max_length=33)
    # purpose = CharField(
    #     max_length=33,
    #     choices=purpose_choices,
    #     default=OTPPurposeTypes.MOBILE_NUMBER_VERIFICATION,
    # )
    expiry_date = DateTimeField(null=True, blank=True)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return str(self.key_name) + "-" + str(self.key_value)


class FriendRequestModel(Model):
    status_choices = (
        (FriendRequestStatus.ACCEPT, "Accept"),
        (FriendRequestStatus.REJECT, "Reject"),
        (FriendRequestStatus.PENDING, "Pending"),
        (FriendRequestStatus.REMOVE, "Remove"),
    )
    sender = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sender_user"
    )
    receiver = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="receiver_user"
    )
    status = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=status_choices,
        default=FriendRequestStatus.PENDING,
    )
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return (
            str(self.sender.email)
            + "-"
            + str(self.receiver.email)
            + "-"
            + str(self.status)
        )


class Product(models.Model):
    category_choices = (
        (ProductCategories.CLOTH, "Cloth"),
        (ProductCategories.ELECTRONIC, "Electronic"),
        (ProductCategories.FOOTWEAR, "FootWear"),
        (ProductCategories.ACCESSORIES, "Accessories"),
        (ProductCategories.STATIONARY, "Stationary"),
    )
    product_id = CharField(
        primary_key=True,
        max_length=255,
        editable=False,
        default=generate_unique_id,
        unique=True,
        null=False,
    )
    user = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_product")
    category = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=category_choices,
        default=ProductCategories.CLOTH,
    )
    name = CharField(max_length=100, null=False, blank=False)
    description = CharField(max_length=300)
    photo = ImageField(
        null=True, blank=True, upload_to=get_product_photo_filepath_with_name
    )
    rent_amount = DecimalField(default=0.0, max_digits=15, decimal_places=4)
    average_ratings = IntegerField(default=0)
    ratings = JSONField(null=True, blank=True)
    is_available = BooleanField(default=True)
    is_active = BooleanField(default=False)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)
    # sharing_type = CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     choices=sharing_types_choices,
    #     default=ProductSharingTypes.SHARE,
    # )

    def __str__(self):
        return str(self.name) + "-" + str(self.category)


class Friends(Model):
    user = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_friends")
    friends_list = TextField(null=True)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return str(self.user.email)


class Quote(models.Model):
    status_choices = (
        (QuoteStatus.PLACED, "Placed"),
        (QuoteStatus.UPDATED, "Updated"),
        (QuoteStatus.APPROVED, "Approved"),
        (QuoteStatus.REJECTED, "Rejected"),
        (QuoteStatus.IN_TRANSIT, "In_Transit"),
        (QuoteStatus.SHARED, "Shared"),
        (QuoteStatus.COMPLETED, "Completed"),
    )
    exchange_types_choices = (
        (QuoteExchangeTypes.RENT, "Rent"),
        (QuoteExchangeTypes.SHARE, "Share"),
        (QuoteExchangeTypes.DEPOSIT, "Deposit"),
    )
    quote_id = CharField(
        primary_key=True,
        max_length=255,
        editable=False,
        default=generate_unique_id,
        unique=True,
        null=False,
    )
    product = ForeignKey(
        Product, on_delete=models.CASCADE, related_name="quote_product"
    )
    owner = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="product_owner"
    )
    customer = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="product_customer"
    )
    last_updated_by = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="last_updated_by"
    )
    status = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=status_choices,
        default=QuoteStatus.PLACED,
    )
    exchange_type = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=exchange_types_choices,
        default=QuoteExchangeTypes.SHARE,
    )
    rent_amount = DecimalField(default=0.0, max_digits=15, decimal_places=4)
    deposit_amount = DecimalField(default=0.0, max_digits=15, decimal_places=4)
    is_rent_paid = BooleanField(default=False)
    is_deposit_paid = BooleanField(default=False)
    meetup_point = CharField(max_length=200)
    from_date = DateField(null=True)
    to_date = DateField(null=True)
    approved_by_owner = BooleanField(default=False)
    approved_by_customer = BooleanField(default=False)
    rejected_by_owner = BooleanField(default=False)
    rejected_by_customer = BooleanField(default=False)
    exchanged_by_owner = BooleanField(default=False)
    exchanged_by_customer = BooleanField(default=False)
    returned_by_owner = BooleanField(default=False)
    returned_by_customer = BooleanField(default=False)
    is_approved = BooleanField(default=False)
    is_exchanged = BooleanField(default=False)
    is_closed = BooleanField(default=False)
    update_count = IntegerField(default=0)
    remarks = TextField(null=True, blank=True)
    customer_ratings = IntegerField(default=0)
    owner_ratings = IntegerField(default=0)
    product_ratings = IntegerField(default=0)
    type_change_history = TextField(null=True)
    remarks_history = TextField(null=True)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return (
            str(self.owner.email)
            + "-"
            + str(self.customer.email)
            + "-"
            + str(self.product.name)
        )


class Notification(models.Model):
    status_choices = (
        (NotificationStatus.READ, "READ"),
        (NotificationStatus.UNREAD, "UNREAD"),
    )
    channel_choices = (
        (NotificationChannel.MOBILE, "MOBILE"),
        (NotificationChannel.EMAIL, "EMAIL"),
        (NotificationChannel.IN_APP, "IN_APP"),
    )
    type_choices = (
        (NotificationType.PRODUCT, "PRODUCT"),
        (NotificationType.FRIEND_REQUEST, "FRIEND_REQUEST"),
        (NotificationType.FRIEND, "FRIEND"),
        (NotificationType.QUOTE, "QUOTE"),
    )
    user = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_notifications"
    )
    text = CharField(max_length=2000)
    status = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=status_choices,
        default=NotificationStatus.UNREAD,
    )
    channel = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=channel_choices,
        default=NotificationChannel.IN_APP,
    )
    type = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=type_choices,
        default=NotificationType.QUOTE,
    )
    type_id = CharField(max_length=100, null=True, blank=True)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return str(self.user.email) + "-" + str(self.channel) + "-" + str(self.type)


class PaymentLink(models.Model):
    status_choices = (
        (PaymentLinkStatus.ACTIVE, "Active"),
        (PaymentLinkStatus.PAID, "Paid"),
        (PaymentLinkStatus.EXPIRED, "Expired"),
    )
    user = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_payment")
    quote = ForeignKey(Quote, on_delete=models.CASCADE, related_name="quote_payment")
    link_id = CharField(
        primary_key=True,
        max_length=255,
        editable=False,
        unique=True,
        null=False,
    )
    link_amount = DecimalField(default=0.0, max_digits=15, decimal_places=4)
    link_purpose = CharField(max_length=200)
    expiry_date = DateTimeField(null=True, blank=True)
    status = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=status_choices,
        default=PaymentLinkStatus.ACTIVE,
    )
    link_url = CharField(max_length=100)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return (
            str(self.user.email)
            + "-"
            + str(self.link_purpose)
            + "-"
            + str(self.expiry_date)
        )


class Message(models.Model):
    sender = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="chat_sender"
    )
    receiver = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="chat_receiver"
    )
    message = CharField(max_length=1200)
    is_read = BooleanField(default=False)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ("created_date",)


class Wallet(models.Model):
    user = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_wallet")
    available_balance = DecimalField(default=0.0, max_digits=15, decimal_places=4)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return str(self.user.email) + "-" + str(self.available_balance)


class Transaction(models.Model):
    status_choices = (
        (TransactionStatus.INITIATED, "Initiated"),
        (TransactionStatus.IN_PROCESS, "In_Process"),
        (TransactionStatus.FAILED, "Failed"),
        (TransactionStatus.COMPLETED, "Completed"),
    )
    type_choices = (
        (TransactionType.CREDIT, "CREDIT"),
        (TransactionType.DEBIT, "DEBIT"),
    )
    source_target_choices = (
        (TransactionSourceTarget.WALLET, "WALLET"),
        (TransactionSourceTarget.BANK, "BANK"),
    )
    from_user = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="from_user_transaction"
    )
    to_user = ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="to_user_transaction"
    )
    quote = ForeignKey(
        Quote, on_delete=models.CASCADE, related_name="transaction_quote", null=True, blank=True
    )
    amount = DecimalField(default=0.0, max_digits=15, decimal_places=4)
    ttype = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=type_choices,
        default=TransactionType.CREDIT,
    )
    status = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=status_choices,
        default=TransactionStatus.COMPLETED,
    )
    source = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=source_target_choices,
        default=TransactionSourceTarget.BANK,
    )
    target = CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=source_target_choices,
        default=TransactionSourceTarget.WALLET,
    )
    remarks = TextField(null=True, blank=True)
    created_date = CreationDateTimeField(null=True)
    updated_date = ModificationDateTimeField(null=True)

    def __str__(self):
        return (
            str(self.from_user.email)
            + "-"
            + str(self.to_user.email)
            + "-"
            + str(self.amount)
        )
