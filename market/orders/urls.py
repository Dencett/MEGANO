from django.urls import path

from orders.views import (
    orders_db_test_view,
    view_test_page,
    OrderDetailView,
    OrderStepOneView,
    OrderStepTwoView,
    OrderStepThreeView,
    OrderHistoryListView,
    UserOrderListView,
)

app_name = "orders"


urlpatterns = [
    path("", view_test_page, name="base"),
    path("test_view/", orders_db_test_view, name="test"),
    path("step_one/", OrderStepOneView.as_view(), name="view_step_one"),
    path("step_two/", OrderStepTwoView.as_view(), name="view_step_two"),
    path("step_three/", OrderStepThreeView.as_view(), name="view_step_three"),
    path("step_four/", OrderStepThreeView.as_view(), name="view_step_four"),
    path("history/", OrderHistoryListView.as_view(), name="history"),
    path("detail/<int:pk>/", OrderDetailView.as_view(), name="detail_order"),
    path("user/order_list/", UserOrderListView.as_view(), name="user_order_list"),
]
