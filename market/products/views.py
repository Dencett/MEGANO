from django.http import HttpRequest, HttpResponse
from django.shortcuts import render  # noqa F401
from django.views import View
from django.views.generic import DetailView

from .services import category_menu
from .models import Product

# Create your views here.


class ExampleView(View):
    """Пример работы"""

    def get(self, request: HttpRequest) -> HttpResponse:
        menu = category_menu()
        context = {
            "menu": menu,
        }
        return render(request, "base.jinja2", context=context)


class ProductDetailsView(DetailView):
    model = Product
    template_name = "products/product_details.jinja2"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = {
            "menu": category_menu(),
        }
        offers = self.object.offer_set.all()
        if offers:
            extra_context["min_price"] = min(offers, key=lambda x: x.price).price
        context.update(extra_context)
        return context
