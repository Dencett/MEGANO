from typing import Any, Dict, Generator

from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from catalog.common import Params
from catalog.utils import Filter, Sorter
from catalog.forms import CatalogFilterForm
from shops.models import Offer


class CatalogListView(ListView):
    """Страница каталога товаров"""

    template_name = "catalog/catalog.jinja2"
    context_object_name = "object_list"
    paginate_by = 8
    pagination_on_each_side = 2
    pagination_on_ends = 1

    def get_queryset(self) -> QuerySet:
        fields = [
            "pk",
            "price",
            "shop_id",
            "product_id",
            "remains",
            "delivery_method",
            "product__name",
            "product__about",
            "product__preview",
            "product__review",
            "product__manufacturer",
            "product__manufacturer__modified_at",
            "product__manufacturer__archived",
            "product__category",
            "product__category__name",
            "product__category__is_active",
            "product__category__archived",
        ]
        select_related_fields = [
            "product",
            "product__manufacturer",
            "product__category",
            "shop",
        ]

        queryset = Offer.objects.select_related(*select_related_fields)

        params = Params(**self.request.GET.dict())

        queryset = self._filter(queryset, params)
        queryset = self._sort(queryset, params)
        return queryset.only(*fields)

    def _filter(self, queryset: QuerySet, params: Params) -> QuerySet:
        filter_manager = Filter(params)
        queryset = filter_manager.filter_offer(queryset)
        return filter_manager.filter_prodict(queryset)

    def _sort(self, queryset: QuerySet, params: Params) -> QuerySet:
        return Sorter(params).sort(queryset)

    def get_context_data(self, *, object_list=None, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(object_list=object_list, **kwargs)
        params = Params(**self.request.GET.dict())

        sort_manager = Sorter(params)
        filter_manager = Filter(params)

        sort_params = sort_manager.build_params()
        filter_params = filter_manager.build_params()

        sort_context = sort_manager.get_context_data()
        filter_context = filter_manager.get_context_data()

        context.update(**sort_context, **filter_context)
        context["pagination_range"] = self.__get_pagination_range(context["paginator"])
        context["sort_params"] = sort_params.to_string()
        context["filter_params"] = filter_params.to_string()
        context["params"] = sort_params + filter_params

        return context

    def __get_pagination_range(self, paginator: Paginator) -> Generator:
        page_number = self.request.GET.get("page")

        if not page_number:
            page_number = 1

        return paginator.get_elided_page_range(
            number=page_number,
            on_each_side=self.pagination_on_each_side,
            on_ends=self.pagination_on_ends,
        )


class CatalogFilteredView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa
        form = CatalogFilterForm(request.POST)
        form.is_valid()

        sort_manager = Sorter(Params(**request.GET.dict()))

        filter_params = Params(**form.cleaned_data)
        params = filter_params + sort_manager.build_params()

        url = reverse("catalog:index")

        if params:
            url += "?" + params

        return redirect(url, permanent=True)


class CatalogHomeView(View):
    def get(self, request, *args, **kwargs):
        view = CatalogListView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CatalogFilteredView.as_view()
        return view(request, *args, **kwargs)
