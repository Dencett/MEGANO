from cart.models import UserOfferCart
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, FormView
from orders.forms import OrderStepTwoForm, OrderStepThreeForm, OrderFastRegistrationAnonymousUser


from orders.models import Order
from profiles.views import UserRegisterView


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_history.jinja2"
    context_object_name = "orders"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/detail_order.jinja2"


def view_test_page(request):
    context = {
        "base": "Базовая страница",
    }
    return render(request, "orders/order_base.jinja2", context=context)


def order_step_one(request):
    context = {"title": "Проверка лички нахой блять!"}
    return render(request, "orders/order_step_one.jinja2", context=context)


def order_step_two(request):
    context = {"title": "Тут перешли на следующий шаг 2"}
    return render(request, "orders/order_step_two.jinja2", context=context)


class OrderStepOneView(UserRegisterView):
    template_name = "orders/order_step_one.jinja2"
    success_url = reverse_lazy("order:order_step_2")
    form_class = OrderFastRegistrationAnonymousUser

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("orders:view_step_two"))

        form = OrderFastRegistrationAnonymousUser()
        super().get(form)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def form_valid(self, form):
        response = super().form_valid(form)

        return response


class OrderStepTwoView(FormView):
    form_class = OrderStepTwoForm
    template_name = "orders/order_step_two.jinja2"

    def form_valid(self, form):
        self.request.session["delivery"] = form.cleaned_data.get("delivery_type")
        self.request.session["city"] = form.cleaned_data.get("city")
        self.request.session["address"] = form.cleaned_data.get("address")

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.request.session.get("delivery"):
            initial["delivery_type"] = self.request.session.get("delivery")

        if self.request.session.get("city"):
            initial["city"] = self.request.session.get("city")

        if self.request.session.get("address"):
            initial["address"] = self.request.session.get("address")

        return initial

    def get_success_url(self):
        return reverse("orders:view_step_three")


class OrderStepThreeView(LoginRequiredMixin, FormView):
    """Отображает страницу третьего шага заказа"""

    form_class = OrderStepThreeForm
    template_name = "orders/order_step_three.jinja2"

    def form_valid(self, form):
        self.request.session["payment"] = form.cleaned_data["payment_type"]
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.request.session.get("payment"):
            initial["payment_type"] = self.request.session.get("payment")
        return initial

    def get_success_url(self):
        return reverse("orders:view_step_four")


class OrderHistoryListView(ListView):
    model = UserOfferCart
    template_name = "orders/order_history.jinja2"
    context_object_name = "orders"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["history"] = Order.objects.filter(carts__user__user_id=self.request.user.pk)
        return context


def orders_db_test_view(request):
    orders = Order.objects.all()
    order = Order.objects.first()
    client = order.carts
    context = {
        "orders": orders,
        "order_first": order,
        # "carts": UserOfferCart.objects.all(),
        "sum_price": order.products_summ_price(),
        "client": client,
    }

    return render(request, "orders/order_test_view.jinja2", context=context)


class UserOrderListView(ListView):
    """Страница отображения заказов пользователя"""

    model = Order
    template_name = "orders/user_order_list.jinja2"
    context_object_name = "order"

    def get_queryset(self):
        queryset = Order.objects.prefetch_related("carts").filter(carts__user__pk=self.request.user.pk)
        return queryset
