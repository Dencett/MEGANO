from typing import Dict, Any

from django.db.models import QuerySet

from products.models import Banner, Category
from shops.models import Offer


class OffersMixin:
    offer_limit = 8
    banner_limit = 3
    foreground_category_limit = 3

    def get_offers_queryset(
        self,
        ordering: str,
        filter_: Dict[str, Any] | None = None,
    ) -> QuerySet:
        if not filter_:
            filter_ = {}

        fields = [
            "price",
            "product",
            "product__id",
            "product__name",
            "product__preview",
            "product__about",
            "product__category",
            "product__category__id",
            "product__category__name",
        ]
        select_related_fields = [
            "product",
            "product__category",
        ]

        return Offer.objects.select_related(*select_related_fields).filter(**filter_).only(*fields).order_by(ordering)

    def get_offers(self) -> QuerySet:
        return self.get_offers_queryset(ordering="?")[: self.offer_limit]

    def get_min_price_product(self) -> QuerySet:
        return self.get_offers_queryset(ordering="price").first()

    def get_limited_products(self) -> QuerySet:
        return self.get_offers_queryset(
            ordering="remains",
            filter_={"remains__gte": 1},
        )[: self.offer_limit]

    def get_banners(self, limit: int = banner_limit) -> QuerySet:
        fields = [
            "name",
            "description",
            "image",
            "archived",
        ]

        return Banner.objects.filter(archived=False).only(*fields).order_by("?")[:limit]

    def get_foreground_category(self, limit: int = foreground_category_limit) -> QuerySet:
        fields = ["foreground"]

        return Category.objects.filter(foreground=True).order_by("?").only(*fields).values_list("id")[:limit]

    def get_min_offers(self):
        foreground_categories = self.get_foreground_category()
        min_offers = []

        for category_id in foreground_categories:
            offer = self.get_offers_queryset(
                ordering="price",
                filter_={"product__category__id__in": category_id},
            ).first()

            if offer:
                min_offers.append(offer)

        return min_offers
