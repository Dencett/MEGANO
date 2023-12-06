import datetime

from django.db.models import Q

from cart.services.cart_service import AnonimCartService
from shops.models import Offer
from products.models import Product
from discount.models import ProductPromo

# Promotion = Callable[[Order], Decimal]
# promos = list[Promotion] = []
#
#
# def promotion(promo: Promotion):
#     promos.append(promo)
#     return promo

# ProductPromo.objects.prefetch_related('categories', 'products').values('categories', 'products').get(pk=1)


class CartDiscount:
    def __init__(self, cart_service: "AnonimCartService"):
        self.cart_service = cart_service
        self.cart = self.cart_service.get_cart_as_dict()
        self.total_price = self.cart_service.get_upd_price()

    def get_sum(self):
        """Метод определения размера скидки"""

        total = self.product()
        return float(total)

    def product(self):
        promos_query = get_product_promo_active_discount()
        total_sale = 0

        for item_id, item_quantity in self.cart.items():
            offer = get_offer_from_db(offer_id=item_id)

            best_discount = {"weight": 0, "value": 0}
            for promo in promos_query:
                # val = promo.value
                # weight = promo.weight
                products_list = get_products_in_promo(promo=promo)
                if offer.product in products_list and promo.weight > best_discount["weight"]:
                    best_discount["weight"], best_discount["value"] = promo.weight, promo.value

            total_sale += get_product_discount(offer.price, item_quantity, best_discount["value"])

        return total_sale


def get_product_discount(price, quantity, sale):
    """
    Метод расчета скидки на товар с учетом кол-ва.
    :param offer_id: int
    :param quantity: int - кол-во товара в корзине
    :param sale: int - процент скидки
    :return: int - вычисленное значение скидки
    """
    total = price * quantity * sale / 100
    return total


def get_offer_from_db(offer_id):
    offer = Offer.objects.get(pk=offer_id)

    return offer


def get_product_promo_active_discount():
    prefetch_fields = ["categories", "products"]
    # TODO оформить фильтр по датам верно от до и тд
    today = datetime.datetime.now(tz=datetime.timezone.utc)
    condition = Q(is_active=True, active_to__gte=today)
    promos_query = ProductPromo.objects.prefetch_related(*prefetch_fields).filter(condition)

    return promos_query


def get_products_in_promo(promo):
    products_list = []

    if promo.products.all():
        for pr in promo.products.all():
            products_list.append(pr)

    if promo.categories.all():
        for category in promo.categories.all():
            products_query = Product.objects.filter(category=category)
            products_list.extend(products_query)

    return products_list
