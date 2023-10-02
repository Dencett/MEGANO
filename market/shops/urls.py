from django.urls import path

from .views import (
    hello_shop_view,
    ShopDetailsView,
    ShopPresentationView,
    ShopProductsList,
    BaseShopView,
    ShopUpdateView,
    # ShopNewOfferCreateView,
)

app_name = "shops"

urlpatterns = [
    path("", hello_shop_view, name="hello"),
    path("base/", BaseShopView.as_view(), name="base"),
    path("<int:pk>/", ShopDetailsView.as_view(), name="shop_detail"),
    # path("products/list/", ShopProductListView.as_view(), name="shop_products"),
    path("<int:pk>/welcome/", ShopPresentationView.as_view(), name="shop_welcome"),
    path("<int:pk>/products/", ShopProductsList.as_view(), name="shop_products"),
    path("<int:pk>/update/", ShopUpdateView.as_view(), name="shop-update"),
    # path("offer-create/", ShopNewOfferCreateView.as_view(), name="offer-create"),
]
