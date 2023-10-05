from django.views.generic import ListView

from shops.models import Offer
from .services.cart_service import get_cart


class CartView(ListView):
    """Корзина пользователя"""

    model = Offer
    cart_name_in_context = "cart_list"
    template_name = "cart/cart.jinja2"

    def get(self, request, *args, **kwargs):
        self.cart = get_cart(request).get_cart_as_list()
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
