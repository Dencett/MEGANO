from django.contrib import admin

from .models import Shop, Offer


class ProductInline(admin.StackedInline):
    model = Shop.products.through


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
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
    search_fields = ["product", "shop"]
