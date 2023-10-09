from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView

from shops.models import Offer
from .services.cart_service import get_cart_service


class CartListView(ListView):
    """Корзина пользователя"""

    model = Offer
    cart_name_in_context = "cart_list"
    template_name = "cart/cart.jinja2"

    def get(self, request, *args, **kwargs):
        self.cart = get_cart_service(request).get_cart_as_list()
        response = super().get(request, *args, **kwargs)
        return response

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


class CartView(View):
    """
    Представление в котором:
        - при полечении "GET" запроса возвращается ProductDetailView.as_view
        - при полечении "POST" запроса возвращается ProductReviewFormView.as_view
    doc: https://docs.djangoproject.com/en/3.2/topics/class-based-views/mixins/#using-formmixin-with-detailview
    """

    def get(self, request, *args, **kwargs):
        view = CartListView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        choice = {"Удалить корзину": RemoveCartView.as_view()}
        action = request.POST.get("action")
        view = choice.get(action)
        return view(request, *args, **kwargs)
