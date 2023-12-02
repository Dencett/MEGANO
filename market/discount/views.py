from django.views.generic import ListView

from .models import SetPromo, ProductPromo, CartPromo


class DiscountListView(ListView):
    template_name = "discount/discount_list.jinja2"
    context_object_name = "promos"
    paginate_by = 12
    models = (SetPromo, ProductPromo, CartPromo)

    # def get_paginate_by(self, queryset: QuerySet) -> int:
    #     """Получение лимита пагинации"""
    #     return self.site_settings.paginate_by

    def get_queryset(self):
        promos = []
        for model in self.models:
            query = model.objects.all()
            promos += query
        # promos.sort TODO сортировка
        return promos
