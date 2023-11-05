from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from orders.models import Order
from .forms import BancAccountForm
from .services.pay_service import pay_order


class PayView(TemplateView):
    template_name = "payapp/base_pay.jinja2"

    def get(self, request, *args, **kwargs):
        order_pk = kwargs["order_pk"]
        order = Order.objects.get(pk=order_pk)
        if order.status != Order.STATUS_CREATED and order.status != Order.STATUS_NOT_PAID:
            return redirect("payapp:status", pk=order_pk)
        if order.payment_type == Order.PAYMENT_TYPES[1][0]:
            # if request.GET.get("button") == "yes":
            kwargs.update({"button": 1})
        return super().get(request, *args, **kwargs)


class PayStatusView(DetailView):
    template_name = "payapp/pay_status.jinja2"
    model = Order
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        order: Order = self.object
        if order.status == Order.STATUS_CREATED:
            redirect("payapp:my_pay", order_pk=order.pk)
        if order.status != Order.STATUS_NOT_PAID:
            context = {"is_order_paid": True}
        else:
            context = {"is_order_paid": False}
        context.update(**kwargs)
        return super().get_context_data(**context)


class BankAccountValidate(View):
    def post(self, request, *args, **kwargs):
        form = BancAccountForm(request.POST)
        order_pk = kwargs.get("order_pk")
        order = Order.objects.get(pk=order_pk)
        if form.is_valid():
            data = form.cleaned_data
            banc_account = int("".join(data["banc_account"].split(" ")))
            host = request.get_host()
            pay_order(order=order, bank_account=banc_account, host_name=host)
        return redirect("payapp:status", pk=order_pk)
