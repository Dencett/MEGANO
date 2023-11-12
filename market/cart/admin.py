from django.contrib import admin
from .models import UserOfferCart


@admin.register(UserOfferCart)
class UserOfferCartAdmin(admin.ModelAdmin):
    list_display = [
        "offer",
        "user",
        "amount",
    ]
