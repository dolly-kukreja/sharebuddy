from django.contrib import admin
from core.models import (
    CustomUser,
    Address,
    OneTimePassword,
    Product,
    FriendRequestModel,
    Friends
)

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Address)
admin.site.register(OneTimePassword)
admin.site.register(Product)
admin.site.register(FriendRequestModel)
admin.site.register(Friends)
