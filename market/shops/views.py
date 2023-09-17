from django.http import HttpRequest
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from shops.models import Shop


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
