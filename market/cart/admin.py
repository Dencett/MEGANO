from cart.models import UserOfferCart
from django.contrib import admin  # noqa


@admin.register(UserOfferCart)
class UserOfferCartAdmin(admin.ModelAdmin):
    list_display = [
        "offer",
        "user",
        "amount",
    ]
