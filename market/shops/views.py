from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, UpdateView


from shops.models import Shop


def hello_shop_view(request: HttpRequest) -> HttpRequest:
    context = {
        "welcome": _("Добро пожаловать в приложение 'Магазины'"),
        "shop_list": Shop.objects.all(),
        "shop": Shop.objects.first(),
    }
    return render(request, "shops/hello_view.jinja2", context=context)


class ShopDetailsView(UserPassesTestMixin, DetailView):
    """
    Подробная страница магазина пользователя.
    Пользователь получает доступ только к своему(своим) магазину.
    Если магазин не связан с пользователем => 403 Forbidden
    """

    model = Shop
    template_name = "shops/shop_detail.jinja2"

    def test_func(self):
        return self.get_object().user == self.request.user or self.request.user.is_superuser


class ShopProductListView(ListView):
    """Представление продуктов магазина"""

    model = Shop
    template_name = "shops/products_list.jinja2"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = Shop.objects.select_related("user").prefetch_related("products").filter(user__id=self.request.user.pk)
        context["shop_offer"] = shop
        return context


class ShopProductsDetail(DetailView):
    """Представление продуктов магазина"""

    model = Shop
    template_name = "shops/shop_products.jinja2"
    context_object_name = "shop"


class ShopUpdateView(UpdateView):
    model = Shop
    fields = ["name", "about", "phone", "email", "avatar"]
    template_name = "shops/shop_form.jinja2"
    context_object_name = "shop"

    def get_success_url(self):
        return reverse(
            "shops:shop_detail",
            kwargs={"pk": self.object.pk},
        )
