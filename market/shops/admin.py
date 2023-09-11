from django.contrib import admin  # noqa F401

from .models import Shop, Offer


class ProductInline(admin.StackedInline):
    model = Shop.products.through


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):  # noqa  F811
    """Админ Магазин"""

    inlines = [
        ProductInline,
    ]

    list_display = (
        "pk",
        "name",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Админ Магазин"""

    list_display = (
        "pk",
        "shop",
        "product",
        "price",
    )
    list_display_links = (
        "pk",
        "price",
    )
    ordering = (
        "pk",
        "price",
    )
