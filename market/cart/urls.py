from django.urls import path
from .views import (
    CartView,
    AddCartFromProduct,
    RemoveOneCartView,
    NewTestView,
)

app_name = "cart"

urlpatterns = [
    path("", CartView.as_view(), name="user_cart"),
    path("add", AddCartFromProduct.as_view(), name="add_cart"),
    path("delete", RemoveOneCartView.as_view(), name="delete_cart"),
    path("test", NewTestView.as_view(), name="test"),
]
