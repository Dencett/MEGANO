from django.contrib import admin  # noqa F401

from .models import SetPromo, Promo, CartPromo


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    """Админ Скидка"""

    list_display = (
        "pk",
        "name",
        "description",
        "value",
        "active_from",
        "active_to",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(SetPromo)
class ProductsSetPromoAdmin(admin.ModelAdmin):
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
    """Админ Привило на корзину"""

    list_display = (
        "pk",
        "name",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)
