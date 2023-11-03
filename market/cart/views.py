from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import Http404, HttpResponse
from django.utils.translation import gettext_lazy as _

from shops.models import Offer
from .forms import UserOneOfferCARTForm
from .services.cart_service import get_cart_service
from .forms import UserOneOfferCARTDeleteForm, UserManyOffersCARTForm


class CartListView(TemplateView):
    """Корзина пользователя"""

    cart_name_in_context = "cart_list"
    template_name = "cart/cart.jinja2"

    def get(self, request, *args, **kwargs):
        self.cart = get_cart_service(request).get_cart_as_list()
        response = super().get(request, *args, **kwargs)
        return response

    def post(self, request, *args, **kwargs):
        self.cart = get_cart_service(request)
        number = self.cart.get_offers_len()
        form = UserManyOffersCARTForm(self.cart.get_offers_len(), request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            data = {form_data[f"offer_id[{i}]"]: form_data[f"amount[{i}]"] for i in range(number)}
            self.cart.update_cart(data)
            return self.get(request, *args, **kwargs)
        else:
            return HttpResponse(form.errors.as_ul(), status=400)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            offers_list = []
            for cart_record in self.cart:
                offers_list.append(cart_record.offer)
            queryset = Offer.objects.all()
        else:
            offers_list = []
            for cart_record in self.cart:
                offers_list.append(cart_record.offer)
            queryset = Offer.objects.all()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {self.cart_name_in_context: self.cart}
        context.update(kwargs)
        return super().get_context_data(object_list=None, **context)


class RemoveCartView(View):
    def post(self, request, *args, **kwargs):
        self.cart = get_cart_service(request)
        self.cart.clear()
        return redirect("cart:user_cart")

    def get(self, request, *args, **kwargs):
        raise Http404


class RemoveOneCartView(View):
    def get(self, request, *args, **kwargs):
        form = UserOneOfferCARTDeleteForm(request.GET)
        if form.is_valid():
            self.cart = get_cart_service(request)
            self.cart.remove_from_cart(**form.cleaned_data)
        return redirect("cart:user_cart")
        # raise Http404


class AddCartFromProduct(View):
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        form = UserOneOfferCARTForm(request.POST)
        self.url = request.META["HTTP_REFERER"]
        self.cart = get_cart_service(request)
        if form.is_valid():
            self.cart.add_to_cart(**form.cleaned_data)
            return redirect(self.url + "#modal_open")
        else:
            return redirect(self.url)


class CartView(View):
    """
    Представление в котором:
        - при полечении "GET" запроса возвращается ProductDetailView.as_view
        - при полечении "POST" запроса возвращается ProductReviewFormView.as_view
    doc: https://docs.djangoproject.com/en/3.2/topics/class-based-views/mixins/#using-formmixin-with-detailview
    """

    BUTTONS = (
        _("Удалить корзину"),
        _("Обновить корзину"),
        _("Оформить заказ"),
    )

    def get(self, request, *args, **kwargs):
        view = CartListView.as_view()
        return view(request, *args, buttons=self.BUTTONS, **kwargs)

    def post(self, request, *args, **kwargs):
        choice = {
            self.BUTTONS[0]: RemoveCartView.as_view(),  # Удалить корзину
            self.BUTTONS[1]: CartListView.as_view(),  # Обновить корзину
            self.BUTTONS[2]: CartListView.as_view(),  # Оформить заказ
        }
        action = request.POST.get("action")
        if action == self.BUTTONS[2]:
            return redirect("orders:view_step_one")
        view = choice.get(action)
        return view(request, *args, buttons=self.BUTTONS, **kwargs)
