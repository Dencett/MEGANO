import datetime
from decimal import Decimal

# from django.db.models import Q, F

from cart.services.cart_service import AnonimCartService
from shops.models import Offer
from products.models import Product
from discount.models import ProductPromo, CartPromo, SetPromo


class CartDiscount:
    def __init__(self, cart_service: "AnonimCartService"):
        self.cart_service = cart_service
        self.cart = self.cart_service.get_cart_as_dict()
        self.total_price = Decimal(self.cart_service.get_upd_price())
        self.today = datetime.datetime.now()

    def __len__(self):
        """Кол-во товаров в корзине"""
        return sum([int(quantity) for quantity in self.cart.values()])

    def get_sum(self):
        """
        Метод определения размера скидки.
        Одновременно может быть применена только одна скидка на корзину или на один набор в корзине.
        Если к корзине не применена скидка ни на корзину, ни на набор,
        то тогда на каждый товар по отдельности ищется скидка на товар,
        при этом на каждый товар может быть применена только одна приоритетная скидка также по весу.
        """

        cart_sale, cart_weight = self._get_cart_promo_discount()
        set_sale, set_weight = self._get_set_promos_discount()

        if cart_weight > set_weight:
            return cart_sale
        elif cart_weight < set_weight:
            return set_sale
        elif cart_weight == set_weight and cart_weight != 0:
            return max(cart_sale, set_sale)
        else:
            products_sale = self._get_product_promos_discount()
            return products_sale

    def _get_product_promos_discount(self):
        """
        Метод определения размера скидки на список товаров
        и/или на указанные категории товаров.
        """
        promos_query = self._get_product_promo_active_discount()
        total_sale = Decimal(0.00)

        for item_id, item_quantity in self.cart.items():
            offer = Offer.objects.get(pk=item_id)
            best_discount = {"weight": 0, "value": 0}

            for promo in promos_query:
                products_list = self._get_products_in_promo(promo=promo)
                if offer.product in products_list and promo.weight > best_discount["weight"]:
                    best_discount["weight"], best_discount["value"] = promo.weight, promo.value

            total_sale += self._get_product_discount(offer.price, item_quantity, best_discount["value"])

        return total_sale

    @classmethod
    def _get_product_discount(cls, price, quantity, value):
        """
        Метод расчета скидки на продукт с учeтом кол-ва.
        :param price: Decimal - стоимость продукта
        :param quantity: int - кол-во товара в корзине
        :param value: int - процент скидки
        :return: Decimal - вычисленное значение скидки
        """
        total = price * quantity * value / 100
        return total

    def _get_product_promo_active_discount(self):
        """
        Получения активных скидок на продукт(ы) и/или категорию(ии)
        """
        prefetch_fields = ["categories", "products"]
        promos_query = ProductPromo.objects.prefetch_related(*prefetch_fields).filter(is_active=True)

        return promos_query

    @classmethod
    def _get_products_in_promo(cls, promo):
        """
        Получение списка товаров.
        """
        products_list = []

        if promo.products.all():
            products_list.extend(promo.products.all())

        if promo.categories.all():
            for category in promo.categories.all():
                products_query = Product.objects.filter(category=category)
                products_list.extend(products_query)

        return products_list

    def _get_cart_promo_discount(self):
        """
        Метод определения размера скидки на корзину.
        """
        promos_query = self._get_cart_promo_active_discount()
        best_discount = {"weight": 0, "value": 0}

        for promo in promos_query:
            if self._is_cart_discount_applicable(promo) and promo.weight > best_discount["weight"]:
                best_discount["weight"], best_discount["value"] = promo.weight, promo.value

        total_sale = self._get_cart_discount(best_discount["value"])
        return total_sale, best_discount["weight"]

    def _get_cart_promo_active_discount(self):
        """
        Получения активных скидок на корзину.
        """

        promos_query = CartPromo.objects.filter(is_active=True)

        return promos_query

    def _get_cart_discount(self, value):
        """
        Метод расчета значения скидки на корзину.
        """
        if value == Decimal(0):
            return Decimal(0)
        elif self.total_price < value:
            return self.total_price - Decimal(1.00)
        else:
            return self.total_price - Decimal(value)

    def _is_cart_discount_applicable(self, promo):  # noqa: C901
        """
        Проверка применима ли скидка на корзины.
        Cкидка применима - возвращается True,
        иначе - False.
        """
        card_items = self.__len__()

        if all([promo.price_from, promo.price_to, promo.items_from, promo.items_to]):
            if (
                card_items in range(promo.items_from, promo.items_to + 1)
                and promo.price_from <= self.total_price <= promo.price_to
            ):
                return True
            return False

        elif all([promo.price_from, promo.price_to, promo.items_to]) and promo.items_from is None:
            if card_items <= promo.items_to and promo.price_from <= self.total_price <= promo.price_to:
                return True
            return False

        elif all([promo.price_from, promo.price_to, promo.items_from]) and promo.items_to is None:
            if card_items >= promo.items_from and promo.price_from <= self.total_price <= promo.price_to:
                return True
            return False

        elif all([promo.items_from, promo.items_to, promo.price_to]) and promo.price_from is None:
            if self.total_price <= promo.price_to and card_items in range(promo.items_from, promo.items_to + 1):
                return True
            return False

        elif all([promo.items_from, promo.items_to, promo.price_from]) and promo.price_to is None:
            if self.total_price >= promo.price_from and card_items in range(promo.items_from, promo.items_to + 1):
                return True
            return False
        #
        elif all([promo.items_from, promo.items_to]) and promo.price_to is None and promo.price_from is None:
            if card_items in range(promo.items_from, promo.items_to + 1):
                return True
            return False

        elif all([promo.price_from, promo.price_to]) and promo.items_from is None and promo.items_to is None:
            if promo.price_from <= self.total_price <= promo.price_to:
                return True
            return False

        elif all([promo.price_to, promo.items_to]) and promo.price_from is None and promo.items_from is None:
            if self.total_price <= promo.price_to and card_items <= promo.items_to:
                return True
            return False

        elif all([promo.price_from, promo.items_from]) and promo.price_to is None and promo.items_to is None:
            if self.total_price >= promo.price_from and card_items >= promo.items_from:
                return True
            return False

        elif all([promo.price_from, promo.items_to]) and promo.price_to is None and promo.items_from is None:
            if self.total_price >= promo.price_from and card_items <= promo.items_to:
                return True
            return False

        elif all([promo.price_to, promo.items_from]) and promo.price_from is None and promo.items_to is None:
            if self.total_price <= promo.price_to and card_items >= promo.items_from:
                return True
            return False
        #
        elif promo.items_from and all([promo.price_from, promo.price_to, promo.items_to]) is False:
            if card_items >= promo.items_from:
                return True
            return False

        elif promo.items_to and all([promo.price_from, promo.price_to, promo.items_from]) is False:
            if card_items <= promo.items_to:
                return True
            return False

        elif promo.price_from and all([promo.price_to, promo.items_from, promo.items_to]) is False:
            if self.total_price >= promo.price_from:
                return True
            return False

        elif promo.price_to and all([promo.price_from, promo.items_from, promo.items_to]) is False:
            if self.total_price <= promo.price_to:
                return True
            return False

        else:
            return False

    def _get_set_promos_discount(self):
        """
        Метод определения размера скидки на наборы.
        """
        promos_query = self._get_set_promo_active_discount()
        best_discount = {"weight": 0, "value": 0}
        cart_products = [Offer.objects.get(pk=offer_id).product for offer_id in self.cart.keys()]

        for promo in promos_query:
            products_dict = self._get_products_in_setpromo(promo)

            if (
                self._is_set_discount_applicable(products_dict, cart_products)
                and promo.weight > best_discount["weight"]
            ):
                best_discount["weight"], best_discount["value"] = promo.weight, promo.value

        total_sale = self._get_set_discount(best_discount["value"])

        return total_sale, best_discount["weight"]

    def _get_set_discount(self, value):
        """
        Метод расчета скидки на набор.
        """

        if value == Decimal(0):
            return Decimal(0)
        elif self.total_price <= value:
            return self.total_price - Decimal(1.00)
        else:
            return Decimal(value)

    def _get_set_promo_active_discount(self):
        """
        Получения активных скидок на наборы.
        """

        prefetch_fields = ["sets__products", "sets__categories"]
        promos_query = SetPromo.objects.prefetch_related(*prefetch_fields).filter(is_active=True)

        return promos_query

    @classmethod
    def _get_products_in_setpromo(cls, promo):
        """
        Получения списка товаров в каждом наборе.
        """
        products_dict = {}

        for item_set in promo.sets.all():
            products_dict[item_set.pk] = []

            if item_set.products.all():
                products_dict[item_set.pk].extend(item_set.products.all())

            for category in item_set.categories.all():
                products_query = Product.objects.filter(category=category)
                products_dict[item_set.pk].extend(products_query)

        return products_dict

    @classmethod
    def _is_set_discount_applicable(cls, products_dict, cart_products):
        """
        Проверка применима ли скидка на набор.
        Cкидка применима - возвращается True,
        иначе - False.
        """
        is_applicable = {}

        for set_id, products in products_dict.items():
            is_applicable[set_id] = False

            for product in cart_products:
                if product in products:
                    is_applicable[set_id] = True
                    break

        return all([status for status in is_applicable.values()])
