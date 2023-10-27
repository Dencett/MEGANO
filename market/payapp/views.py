from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from .models import TestOrder
from .forms import BancAccountForm
from .services.pay_service import pay_order


class PayView(TemplateView):
    template_name = "payapp/base_pay.jinja2"

    def get(self, request, *args, **kwargs):
        order_pk = kwargs["order_pk"]
        order = TestOrder.objects.get(pk=order_pk)
        if order.status_payed:
            return redirect("payapp:status", pk=order_pk)
        if request.GET.get("button") == "yes":
            kwargs.update({"button": 1})
        return super().get(request, *args, **kwargs)


class PayStatusView(DetailView):
    template_name = "payapp/pay_status.jinja2"
    model = TestOrder
    context_object_name = "order"


class BankAccountValidate(View):
    def post(self, request, *args, **kwargs):
        form = BancAccountForm(request.POST)
        order_pk = kwargs.get("order_pk")
        order = TestOrder.objects.get(pk=order_pk)
        if form.is_valid():
            data = form.cleaned_data
            banc_account = int("".join(data["banc_account"].split(" ")))
            pay_order(order=order, bank_account=banc_account)
        return redirect("payapp:status", pk=order_pk)
