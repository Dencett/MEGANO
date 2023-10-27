from django.urls import path

from .views import PayView, PayStatusView, BankAccountValidate


app_name = "payapp"

urlpatterns = [
    path("mypay/<int:order_pk>/", PayView.as_view(), name="my_pay"),
    path("status/<int:pk>/", PayStatusView.as_view(), name="status"),
    path("acc/<int:order_pk>/", BankAccountValidate.as_view(), name="acc"),
]
