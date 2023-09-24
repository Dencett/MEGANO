from django.urls import path

from .views import (
    hello_shop_view,
    ShopDetailsView,
    ShopProductListView,
)

app_name = "shops"

urlpatterns = [
    path("", hello_shop_view, name="hello"),
    path("<int:pk>/", ShopDetailsView.as_view(), name="shop_detail"),
    path("products/list/", ShopProductListView.as_view(), name="shop_products"),
]
