from django.contrib import admin  # noqa F401

from .models import SetPromo, ProductPromo, CartPromo


@admin.register(ProductPromo)
class ProductPromoAdmin(admin.ModelAdmin):
    """Админ Скидка"""

    list_display = (
        "pk",
        "name",
        "description",
        # "value",
        # "active_from",
        # "active_to",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(SetPromo)
class SetPromoAdmin(admin.ModelAdmin):
    """Админ Набор"""

    list_display = (
        "pk",
        "name",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(CartPromo)
class CartPromoAdmin(admin.ModelAdmin):
    """Админ"""

    list_display = (
        "pk",
        "name",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)
