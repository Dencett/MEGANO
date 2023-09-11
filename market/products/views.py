from django.http import HttpRequest, HttpResponse
from django.shortcuts import render  # noqa F401
from django.views import View

from .services import category_menu

# Create your views here.


class ExampleView(View):
    """Пример работы"""

    def get(self, request: HttpRequest) -> HttpResponse:
        menu = category_menu()
        context = {
            "menu": menu,
        }
        return render(request, "base.jinja2", context=context)
