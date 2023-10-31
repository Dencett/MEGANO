from types import NoneType

from django.db import transaction
from orders.models import Order, OrderDetail
from profiles.models import User
from shops.models import Offer
from config import settings


class OrderServices:
    def __init__(self, request):
        self.request = request

    def get_last_order(self) -> Order:
        return Order.objects.filter(carts__user_user_id=self.request.pk)


class OrderDetailCreate:
    """Клас для работы с заказами"""

    def __init__(self, request):
        self.user = request.user
        self.request = request
        self.session = request.session.get(settings.CART_SESSION_KEY)

    def get_products_in_cart(self):
        """Показать продукты, которые находятся в корзине в ссесиях"""

        multiselect = self.session.keys()
        products = Offer.objects.filter(pk__in=multiselect)
        return products

    def create_order(self):
        """Метод создания заказа после прохождения форм опроса пользователя"""
        # multiselect = self.session.keys()
        # products = Offer.objects.filter(pk__in=multiselect)

        user = User.objects.filter(pk=self.request.user.pk).first()
        delivery_type = self.request.session["delivery_type"]
        city = self.request.session["city"]
        address = self.request.session["address"]
        payment_type = self.request.session["payment_type"]

        order = Order.objects.create(
            city=city,
            address=address,
            user=user,
            delivery_type=delivery_type,
            # order_number=self.get_last_order_number(),
            payment_type=payment_type,
            status=Order.STATUS_CREATED,
        )
        return order

    def get_last_order_number(self):
        """
        Метод получает последний номер заказа пользователя.
        Присваивает следующий порядковый номер созданному заказу.
        # В разработке...
        """
        user = User.objects.get(pk=self.request.user.pk)
        order_number = Order.objects.filter(user=user).first().order_number
        try:
            if order_number is None:
                order_number = 1
                return order_number
        except NoneType as exc:
            return f"{exc.__class__, exc.__class__.__name__, exc}"

        order_number += 1
        return order_number

    @transaction.atomic
    def created_order_details_product(self):
        """Метод добавления продуктов из корзины"""
        # multiselect = self.session.keys()
        # products = Offer.objects.filter(pk__in=multiselect)
        order = self.create_order()

        for offer, value in self.session.items():
            add_offer = Offer.objects.get(pk=offer)
            OrderDetail.objects.create(offer=add_offer, quantity=value, user_order=order)
