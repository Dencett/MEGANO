from django.contrib import admin  # noqa
from .models import UserOfferCart

# Register your models here.


@admin.register(UserOfferCart)
class UserOfferCartAdmin(admin.ModelAdmin):
    list_display = [
        "offer",
        "user",
        "amount",
    ]
