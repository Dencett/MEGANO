from django.http import HttpRequest
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from shops.models import Shop, Offer


# #### test-view for base template ####
# def base_view(request: HttpRequest):
#     context = {}
#     return render(request, "base.jinja", context=context)


def hello_shop_view(request: HttpRequest) -> HttpRequest:
    context = {
        "welcome": _("Добро пожаловать в приложение 'Магазины'"),
        "shop_list": Shop.objects.all(),
        "shop": Shop.objects.first(),
    }
    return render(request, "shops/hello_view.jinja2", context=context)


class ShopDetailsView(DetailView):
    model = Shop
    template_name = "shops/shop_detail.jinja2"


class ShopProductListView(ListView):
    model = Offer
    template_name = "shops/products_list.jinja2"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = Shop.objects.filter(user__id=self.request.user.pk)
        context["shop_offer"] = shop
        # context['offer'] = (Offer.objects
        #                     .select_related("shop")
        #                     .prefetch_related("product")
        #                     .filter(shop__user=shop)
        #                     )

        # Offer.objects.select_related("shop").prefetch_related("product").all()
        # offers.filter(shop__name="DNS")

        return context
