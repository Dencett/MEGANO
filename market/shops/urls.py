from django.urls import path

from .views import (
    hello_shop_view,
    ShopDetailsView,
)

app_name = "shops"

urlpatterns = [
    path("", hello_shop_view, name="hello"),
    path("shop/<int:pk>/", ShopDetailsView.as_view(), name="shop_detail"),
]
