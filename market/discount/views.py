import datetime

from django.db.models import QuerySet, Q, Value, CharField
from django.views.generic import ListView, DetailView


from .models import SetPromo, ProductPromo, CartPromo, BasePromo
from site_settings.models import SiteSettings


class DiscountListView(ListView):
    template_name = "discount/discount_list.jinja2"
    context_object_name = "promos"
    models = (SetPromo, ProductPromo, CartPromo)

    @property
    def site_settings(self) -> SiteSettings:
        """Получение настроек"""
        return SiteSettings.load()

    def get_paginate_by(self, queryset: QuerySet) -> int:
        """Получение лимита пагинации"""
        return self.site_settings.paginate_by

    def get_queryset(self):
        fields = "name", "description", "active_from", "active_to", "preview", "is_active", "pk"
        today = datetime.datetime.now(tz=datetime.timezone.utc)
        condition = Q(is_active=True, active_to__gte=today)
        disc_type = {
            "setpromo": Value("setpromo", output_field=CharField()),
            "productpromo": Value("productpromo", output_field=CharField()),
            "cartpromo": Value("cartpromo", output_field=CharField()),
        }

        promos = (
            SetPromo.objects.annotate(disc_type=disc_type["setpromo"])
            .filter(condition)
            .union(ProductPromo.objects.annotate(disc_type=disc_type["productpromo"]).filter(condition))
            .union(CartPromo.objects.annotate(disc_type=disc_type["cartpromo"]).filter(condition))
            .values_list(*fields, "disc_type", named=True)
            .order_by("active_from")
        )
        return promos

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_method"] = BasePromo.preview.field.storage.url
        return context


class SetPromoView(DetailView):
    model = SetPromo
    template_name = "discount/setpromo.jinja2"


class ProductPromoView(DetailView):
    model = ProductPromo
    template_name = "discount/productpromo.jinja2"


class CartPromoView(DetailView):
    model = CartPromo
    template_name = "discount/cartpromo.jinja2"
