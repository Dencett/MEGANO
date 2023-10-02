from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

# from shops.forms import OfferCreateForm

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


class ShopDetailsView(PermissionRequiredMixin, DetailView):
    model = Shop
    template_name = "shops/shop_detail.jinja2"
    permission_required = (
        "shops.add_shop",
        "shops.change_shop",
        "shops.delete_shop",
        "shops.view_shop",
    )

    def has_permission(self):
        return self.get_object().user == self.request.user or self.request.user.is_superuser


class ShopProductListView(ListView):
    # модель поменя => Шаблон поменять

    model = Offer
    template_name = "shops/products_list.jinja2"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = Shop.objects.select_related("user").prefetch_related("products").filter(user__id=self.request.user.pk)
        context["shop_offer"] = shop
        return context


# class ShopPresentationView(TemplateView):
class ShopPresentationView(DetailView):
    template_name = "shops/shop_welcome.jinja2"
    model = Shop

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user = self.request.user.pk
    #     context['shop_det'] = Shop.objects.filter(user=user).all()
    #     return context


class ShopProductsList(DetailView):
    model = Shop
    template_name = "shops/shop_products.jinja2"
    context_object_name = "shop_prod"


class BaseShopView(TemplateView):
    template_name = "shops/base_shop.jinja2"


class ShopUpdateView(UpdateView):
    model = Shop
    fields = ["name", "about", "phone", "email", "avatar", "products"]
    template_name = "shops/shop_form.jinja2"
    context_object_name = "shop"

    # success_url = reverse_lazy("shops:shop_detail")
    def get_success_url(self):
        return reverse(
            "shops:shop_detail",
            kwargs={"pk": self.object.pk},
        )


# class ShopNewOfferCreateView(TemplateView):
#     template_name = "shops/shops_offer_create.jinja2"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["user_shop_offer"] = (
#             Offer.objects.prefetch_related("product").select_related("shop").filter(shop__user_id=self.request.user.pk)
#         )
#         context["form"] = OfferCreateForm()
#         return context
