from django.contrib import admin
from core.models import (
    CustomUser,
    Address,
    OneTimePassword,
    Product,
    FriendRequestModel,
    Friends,
    Quote,
    Notification,
    Message,
)

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Address)
admin.site.register(OneTimePassword)
admin.site.register(Product)
admin.site.register(FriendRequestModel)
admin.site.register(Friends)
admin.site.register(Quote)
admin.site.register(Notification)
admin.site.register(Message)
