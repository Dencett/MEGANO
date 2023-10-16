from typing import Union

from django.db.models import Sum
from django.http import HttpRequest
from django.conf import settings
from django.db.models import F

from cart.models import UserOfferCart
from shops.models import Offer


class AnonimServiceException(Exception):
    pass


class AnonimCartService:
    """Сервис корзины для анонимного пользователя. Все записи, цена и кол-во товара хранятся в сессии"""

    def __init__(self, request: HttpRequest):
        self.session = request.session
        session_cart = self.session.get(settings.CART_SESSION_KEY)
        if not session_cart:
            session_cart = self.session[settings.CART_SESSION_KEY] = {}
        self.session_cart = session_cart

        session_cart_length = self.session.get(settings.CART_SIZE_SESSION_KEY)
        if not session_cart_length:
            self.session[settings.CART_SIZE_SESSION_KEY] = "0"
        self.session_cart_length = self.session[settings.CART_SIZE_SESSION_KEY]

        session_cart_price = self.session.get(settings.CART_PRICE_SESSION_KEY)
        if not session_cart_price:
            self.session[settings.CART_PRICE_SESSION_KEY] = "0.00"
        self.session_cart_price = self.session[settings.CART_PRICE_SESSION_KEY]

    def _save_cart(self):
        self.session.modified = True

    def _change_session_cart_length(self, amount: Union[str, int], add: bool = True):
        cart_size = int(self.session[settings.CART_SIZE_SESSION_KEY])
        if add:
            self.session[settings.CART_SIZE_SESSION_KEY] = str(cart_size + int(amount))
        else:
            self.session[settings.CART_SIZE_SESSION_KEY] = str(cart_size - int(amount))

    def _change_session_cart_price(self, money: Union[str, float], add: bool = True):
        cart_price = float(self.session[settings.CART_PRICE_SESSION_KEY])
        if add:
            self.session[settings.CART_PRICE_SESSION_KEY] = "{:.2f}".format(cart_price + float(money))
        else:
            self.session[settings.CART_PRICE_SESSION_KEY] = "{:.2f}".format(cart_price - float(money))

    def get_cart_as_list(self):
        """Получает список из UserOfferCart без атрибута user на основании сессии"""
        cart = []
        if not self.session_cart:
            return cart
        for offer_pk, amount in self.session_cart.items():
            record = UserOfferCart(offer_id=int(offer_pk), amount=amount)
            cart.append(record)
        return cart

    def remove_from_cart(self, offer_id: int):
        """
        Удаляет одну запись(Offer) активной корзины
        :param offer_id: Offer.pk - ID модели Offer
        :return:
        """
        try:
            current_amount = self.session_cart.pop(str(offer_id))

            self._change_session_cart_length(amount=current_amount, add=False)

            offer = Offer.objects.get(pk=offer_id)
            self._change_session_cart_price(money=offer.price * int(current_amount), add=False)
            self._save_cart()
        except KeyError:
            return

    def add_to_cart(self, offer_id: int, amount: Union[int, str] = 1):
        """
        Добавляет к существующей корзине запись, если такая запись уже существует добавляет количество.
        :param offer_id:
        :param amount:
        :return:
        """
        current_amount = int(self.session_cart.get(str(offer_id), "0"))
        self.session_cart[str(offer_id)] = str(current_amount + int(amount))
        self._change_session_cart_length(amount=amount)
        offer = Offer.objects.get(pk=offer_id)
        self._change_session_cart_price(money=offer.price * int(amount))
        self._save_cart()

    def change_amount(self, offer_id: int, amount: int):
        """
        Изменяет количество в существующей записи корзине
        :param offer_id:
        :param amount:
        :return:
        """
        current_amount = self.session_cart.get(str(offer_id))
        if not current_amount:
            raise UserOfferCart.DoesNotExict("Такого предложения не найдено в корзине")
        offer = Offer.objects.get(pk=offer_id)
        current_amount = int(current_amount)
        self._change_session_cart_length(amount=(amount - current_amount))
        self._change_session_cart_price(money=offer.price * (amount - current_amount))

        self.session_cart[str(offer_id)] = str(amount)
        self._save_cart()

    def update_cart(self, data: dict):
        """
        Изменяет анонимную корзину согласно переданному словарю. Данные предыдущей корзины удаляться.
        :param data:  is dict where key = offer_id; value = amount например data = {Offer.pk: amount, ... }
        :return:
        """
        new_data = {}
        cart_size = 0
        for k, v in data.items():
            if v > 0:
                new_data[str(k)] = str(v)
                cart_size += v
        self.session_cart = self.session[settings.CART_SESSION_KEY] = new_data
        self.session[settings.CART_SIZE_SESSION_KEY] = str(cart_size)
        self._update_price()
        self._save_cart()

    def _update_price(self):
        sum_price = 0
        offers_dict = Offer.objects.filter(pk__in=self.session_cart.keys()).only("price").in_bulk(field_name="id")
        for str_offer_id, str_amount in self.session_cart.items():
            price = offers_dict[int(str_offer_id)].price
            sum_price += price * int(str_amount)
        self.session[settings.CART_PRICE_SESSION_KEY] = str(sum_price)
        self._save_cart()

    def get_upd_price(self):
        """Обновляет цену для всей корзины на основе данных из БД и возвращает это значение"""
        self._update_price()
        return self.session[settings.CART_PRICE_SESSION_KEY]

    def get_upd_length(self):
        """Обновляет кол-во товара для всей корзины на основе данных в сессии и возвращает это значение"""
        length = 0
        for amount in self.session_cart.values():
            length += int(amount)
        self.session[settings.CART_SIZE_SESSION_KEY] = str(length)
        self._save_cart()
        return length

    def get_offers_len(self) -> int:
        """Возвращает количество записей в корзине сессии"""
        length = len(self.session_cart)
        return length

    def __len__(self):
        """Возвращает значение равное кол-ву товара хранимое в сессии session['cart_size"]"""
        return int(self.session[settings.CART_SIZE_SESSION_KEY])

    def clear(self):
        """Удаляет и обнуляет анонимную корзину"""
        self.session_cart.clear()
        self._save_cart()
        self.session[settings.CART_SIZE_SESSION_KEY] = "0"
        self.session[settings.CART_PRICE_SESSION_KEY] = "0.00"

    def append_cart_to_history(self):
        """Не применимо к анонимной корзине. функция для сохранения записей корзины в истории"""
        raise AnonimServiceException(
            "Такой метод недопустим для анонимной корзины",
        )


class UserCartService:
    """
    Класс для сервиса пользовательской корзины.
    Кол-во товара и цена активной корзины хранятся в сессии.
    Записи корзины хранятся в БД модель UserOfferCart.
    если поле записи is_active = True, то запись попадает в текущую корзину пользователя. иначе записи хранятся,
    как журнал на записи которого ссылается модель Заказа.
    """

    def __init__(self, request: HttpRequest):
        self.user = request.user
        self.session = request.session
        session_cart_length = self.session.get(settings.CART_SIZE_SESSION_KEY)
        if not session_cart_length:
            self.session[settings.CART_SIZE_SESSION_KEY] = "0"
            self._save_cart()
        self.session_cart_length = self.session[settings.CART_SIZE_SESSION_KEY]

        session_cart_price = self.session.get(settings.CART_PRICE_SESSION_KEY)
        if not session_cart_price:
            self.session[settings.CART_PRICE_SESSION_KEY] = "0.00"
            self._save_cart()
        self.session_cart_price = self.session[settings.CART_PRICE_SESSION_KEY]

    def _change_session_cart_length(self, amount: Union[str, int], add: bool = True):
        cart_size = int(self.session[settings.CART_SIZE_SESSION_KEY])
        if add:
            self.session[settings.CART_SIZE_SESSION_KEY] = str(cart_size + int(amount))
        else:
            self.session[settings.CART_SIZE_SESSION_KEY] = str(cart_size - int(amount))
        self.session.modified = True

    def _change_session_cart_price(self, money: Union[str, float], add: bool = True):
        cart_price = float(self.session[settings.CART_PRICE_SESSION_KEY])
        if add:
            self.session[settings.CART_PRICE_SESSION_KEY] = "{:.2f}".format(cart_price + float(money))
        else:
            self.session[settings.CART_PRICE_SESSION_KEY] = "{:.2f}".format(cart_price - float(money))

    def get_cart_as_list(self) -> list:
        """Возвращает список с активными записями корзины из БД"""
        return list(UserOfferCart.objects.filter(user=self.user, is_active=True).select_related("offer"))

    def remove_from_cart(self, offer_id: int):
        """Удаляет активную запись корзины c полученным Offer.id"""
        try:
            cart_record = UserOfferCart.objects.select_related("offer").get(
                user=self.user, offer_id=offer_id, is_active=True
            )
            current_amount = cart_record.amount
            self._change_session_cart_length(current_amount, add=False)
            self._change_session_cart_price(cart_record.offer.price * current_amount, add=False)
            cart_record.delete()
            self._save_cart()
        except UserOfferCart.DoesNotExist:
            return
        except UserOfferCart.MultipleObjectsReturned:
            cart_records = UserOfferCart.objects.filter(
                user=self.user, offer_id=offer_id, is_active=True
            ).select_related("offer")
            current_amount = sum([record.amount for record in cart_records])
            current_price = sum([record.offer.price * record.amount for record in cart_records])
            self._change_session_cart_length(current_amount, add=False)
            self._change_session_cart_price(current_price, add=False)
            cart_records.delete()

    def add_to_cart(self, offer_id: int, amount=1):
        """Добавляет к существующей активной записи корзины на основе offer_id количество amount,
        или создает запись с соответствующим offer; amount
        """
        try:
            cart_record = UserOfferCart.objects.get(user=self.user, offer_id=offer_id, is_active=True)
            cart_record.amount += amount
            cart_record.save()
        except UserOfferCart.DoesNotExist:
            cart_record = UserOfferCart(user=self.user, offer_id=offer_id, amount=amount, is_active=True)
            cart_record.save()
        self._change_session_cart_length(cart_record.amount)
        self._change_session_cart_price(cart_record.offer.price * cart_record.amount)

    def change_amount(self, offer_id: int, amount: int):
        """
        Изменяет количество для уже существующей активной записи корзины на основе offer_id
        :param offer_id:
        :param amount:
        :return:
        """
        cart_record = UserOfferCart.objects.get(user=self.user, offer_id=offer_id, is_active=True).select_related(
            "offer"
        )
        current_amount = cart_record.amount
        cart_record.amount = int(amount)
        self._change_session_cart_length(amount - current_amount)
        self._change_session_cart_price(cart_record.offer.price * (amount - current_amount))
        cart_record.save()
        # self._change_session_cart_length(amount)
        self._save_cart()

    def update_cart(self, data: dict):
        """
        Изменяет активную корзину пользователя согласно переданному словарю. Данные предыдущей корзины удаляться.
        :param data:  is dict where key = offer_id; value = amount например data = {Offer.pk: amount, ... }
        :return:
        """
        current_cart = self.get_cart_as_list()
        remove_list = []
        update_list = []
        for cart_record in current_cart:
            if cart_record.offer_id in data:
                amount = data[cart_record.offer_id]
                if amount <= 0:
                    remove_list.append(cart_record.pk)
                elif amount != cart_record.amount:
                    cart_record.amount = amount
                    update_list.append(cart_record)
        if update_list or remove_list:
            if update_list:
                UserOfferCart.objects.bulk_update(update_list, ["amount"])
            if remove_list:
                UserOfferCart.objects.filter(id__in=remove_list).delete()
            self.get_upd_length()
            self._update_price()

    def _update_price(self):
        sum_price = (
            UserOfferCart.objects.filter(user=self.user, is_active=True)
            .select_related("offer")
            .annotate(sum_price=(F("amount") + 0) * F("offer__price"))
            .aggregate(Sum("sum_price"))
            .get("sum_price__sum")
        )
        self.session[settings.CART_PRICE_SESSION_KEY] = str(sum_price)
        self._save_cart()

    def get_upd_price(self):
        """Обновляет цену для всей корзины на основе данных из БД и возвращает это значение"""
        self._update_price()
        return self.session[settings.CART_PRICE_SESSION_KEY]

    def get_upd_length(self) -> int:
        """Обновляет кол-во товара для всей корзины на основе данных БД и возвращает это значение"""
        length = (
            UserOfferCart.objects.filter(user=self.user, is_active=True).aggregate(Sum("amount")).get("amount__sum")
        )
        if not length:
            length = 0
        self.session[settings.CART_SIZE_SESSION_KEY] = str(length)
        self._save_cart()
        return length

    def get_offers_len(self) -> int:
        """Возвращает количество активных записей в корзине"""
        return UserOfferCart.objects.filter(user=self.user, is_active=True).count()

    def __len__(self):
        """Возвращает значение равное кол-ву товара в корзине хранимое в сессии session['cart_size"]"""
        return int(self.session[settings.CART_SIZE_SESSION_KEY])

    def clear(self):
        """Удаляет все активные записи корзины, обнуляет корзину"""
        queryset = UserOfferCart.objects.filter(user=self.user, is_active=True).all()
        queryset.delete()
        self.session[settings.CART_SIZE_SESSION_KEY] = "0"
        self.session[settings.CART_PRICE_SESSION_KEY] = "0.00"
        self._save_cart()

    def _save_cart(self):
        self.session.modified = True

    def append_cart_to_history(self, cart_records: list = None):
        """
        Сохраняет активных записей корзины в не активные, эти записи дальше используются для хранения модели ЗАКАЗА.
        Если не передан параметр cart_records, то переводит все активные записи текущего пользователя.
        :param cart_records: список [UserOfferCart, ]
        :return:
        """
        if not cart_records:
            cart_records = self.get_cart_as_list()
        for records in cart_records:
            records.is_active = False
        UserOfferCart.objects.bulk_update(cart_records, ["is_active"])
        self.session[settings.CART_SIZE_SESSION_KEY] = "0"
        self.session[settings.CART_PRICE_SESSION_KEY] = "0.00"
        self._save_cart()


def _merge_session_cart_to_user_cart(request: HttpRequest, anonim_cart: AnonimCartService):
    user_cart = UserCartService(request)
    session_cart_as_dict = anonim_cart.session_cart
    for offer_id, amount in session_cart_as_dict.items():
        user_cart.add_to_cart(int(offer_id), int(amount))
    anonim_cart.clear()
    user_cart.get_upd_length()
    user_cart.get_upd_price()
    return user_cart


def get_cart_service(request: HttpRequest) -> Union[UserCartService, AnonimCartService]:
    """Функция для получения сервиса для работы с корзиной. Если пользователь анонимный,
    то возвращает сервис для Анонимной корзины работающий на сессиях. Иначе возвращает сервис для корзины пользователя,
    работающий через БД.
    """
    if request.user.is_anonymous:
        return AnonimCartService(request)
    else:
        return UserCartService(request)


def login_cart(request: HttpRequest) -> None:
    """Обновление пользовательской корзины при входе пользователя, все записи анонимной корзины мигрируют в
    пользовательскую корзину"""
    anonim_cart = AnonimCartService(request)
    if anonim_cart.session_cart:
        user_cart = _merge_session_cart_to_user_cart(request, anonim_cart)
    else:
        user_cart = get_cart_service(request)
    user_cart.get_upd_length()
    return
