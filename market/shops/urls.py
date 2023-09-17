from django.urls import path

from .views import (
    hello_shop_view,
)

app_name = "shops"

urlpatterns = [
    path("", hello_shop_view, name="hello"),
]
