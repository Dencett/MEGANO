from typing import Union

from django.db.models import Sum
from django.http import HttpRequest
from django.conf import settings
from django.db.models import F

from cart.models import UserOfferCart
from shops.models import Offer


class AnonimCartService:
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
        cart = []
        if not self.session_cart:
            return cart
        for offer_pk, amount in self.session_cart.items():
            record = UserOfferCart(offer_id=int(offer_pk), amount=amount)
            cart.append(record)
        return cart

    def remove_from_cart(self, offer_id: int):
        try:
            current_amount = self.session_cart.pop(str(offer_id))

            self._change_session_cart_length(amount=current_amount, add=False)

            offer = Offer.objects.get(pk=offer_id)
            self._change_session_cart_price(money=offer.price * int(current_amount), add=False)
            self._save_cart()
        except KeyError:
            return

    def add_to_cart(self, offer_id: int, amount: Union[int, str] = 1):
        current_amount = int(self.session_cart.get(str(offer_id), "0"))
        self.session_cart[str(offer_id)] = str(current_amount + int(amount))
        self._change_session_cart_length(amount=amount)
        offer = Offer.objects.get(pk=offer_id)
        self._change_session_cart_price(money=offer.price * int(amount))
        self._save_cart()

    def change_amount(self, offer_id: int, amount: int):
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

        :param data: is dict where key = offer_id; value = amount
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
        self._update_price()
        return self.session[settings.CART_PRICE_SESSION_KEY]

    def get_upd_length(self):
        length = 0
        for amount in self.session_cart.values():
            length += int(amount)
        self.session[settings.CART_SIZE_SESSION_KEY] = str(length)
        self._save_cart()
        return length

    def get_offers_len(self) -> int:
        length = len(self.session_cart)
        return length

    def __len__(self):
        return int(self.session[settings.CART_SIZE_SESSION_KEY])

    def clear(self):
        self.session_cart.clear()
        self._save_cart()
        self.session[settings.CART_SIZE_SESSION_KEY] = "0"
        self.session[settings.CART_PRICE_SESSION_KEY] = "0.00"


class UserCartService:
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
        return list(UserOfferCart.objects.filter(user=self.user))

    def remove_from_cart(self, offer_id: int):
        try:
            cart_record = UserOfferCart.objects.select_related("offer").get(user=self.user, offer_id=offer_id)
            current_amount = cart_record.amount
            self._change_session_cart_length(current_amount, add=False)
            self._change_session_cart_price(cart_record.offer.price * current_amount, add=False)
            cart_record.delete()
            self._save_cart()
        except UserOfferCart.DoesNotExist:
            return
        except UserOfferCart.MultipleObjectsReturned:
            cart_records = UserOfferCart.objects.filter(user=self.user, offer_id=offer_id).select_related("offer")
            current_amount = sum([record.amount for record in cart_records])
            current_price = sum([record.offer.price * record.amount for record in cart_records])
            self._change_session_cart_length(current_amount, add=False)
            self._change_session_cart_price(current_price, add=False)
            cart_records.delete()

    def add_to_cart(self, offer_id: int, amount=1):
        try:
            cart_record = UserOfferCart.objects.get(user=self.user, offer_id=offer_id)
            cart_record.amount += amount
            cart_record.save()
        except UserOfferCart.DoesNotExist:
            cart_record = UserOfferCart(user=self.user, offer_id=offer_id, amount=amount)
            cart_record.save()
        self._change_session_cart_length(cart_record.amount)
        self._change_session_cart_price(cart_record.offer.price * cart_record.amount)

    def change_amount(self, offer_id: int, amount: int):
        cart_record = UserOfferCart.objects.get(user=self.user, offer_id=offer_id).select_related("offer")
        current_amount = cart_record.amount
        cart_record.amount = int(amount)
        self._change_session_cart_length(amount - current_amount)
        self._change_session_cart_price(cart_record.offer.price * (amount - current_amount))
        cart_record.save()
        # self._change_session_cart_length(amount)
        self._save_cart()

    def update_cart(self, data: dict):
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
        sum_price = 0
        sum_price = (
            UserOfferCart.objects.select_related("offer")
            .annotate(sum_price=(F("amount") + 0) * F("offer__price"))
            .aggregate(Sum("sum_price"))
            .get("sum_price__sum")
        )
        self.session[settings.CART_PRICE_SESSION_KEY] = str(sum_price)
        self._save_cart()

    def get_upd_price(self):
        self._update_price()
        return self.session[settings.CART_PRICE_SESSION_KEY]

    def get_upd_length(self) -> int:
        length = UserOfferCart.objects.filter(user=self.user).aggregate(Sum("amount")).get("amount__sum")
        if not length:
            length = 0
        self.session[settings.CART_SIZE_SESSION_KEY] = str(length)
        self._save_cart()
        return length

    def get_offers_len(self) -> int:
        return UserOfferCart.objects.filter(user=self.user).count()

    def __len__(self):
        return int(self.session[settings.CART_SIZE_SESSION_KEY])

    def clear(self):
        queryset = UserOfferCart.objects.filter(user=self.user).all()
        queryset.delete()
        self.session[settings.CART_SIZE_SESSION_KEY] = "0"
        self.session[settings.CART_PRICE_SESSION_KEY] = "0.00"
        self._save_cart()

    def _save_cart(self):
        self.session.modified = True


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
    """Функция для получения сервиса для работы с корзиной"""
    if request.user.is_anonymous:
        return AnonimCartService(request)
    else:
        return UserCartService(request)


def login_cart(request: HttpRequest) -> None:
    """Обновление пользовательской корзины при входе пользователя"""
    anonim_cart = AnonimCartService(request)
    if anonim_cart.session_cart:
        user_cart = _merge_session_cart_to_user_cart(request, anonim_cart)
    else:
        user_cart = get_cart_service(request)
    user_cart.get_upd_length()
    return
