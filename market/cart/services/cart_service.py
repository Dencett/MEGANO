from django.http import HttpRequest
from django.conf import settings
from typing import Union

from cart.models import UserOfferCART


class AnonimCart:
    def __init__(self, request: HttpRequest):
        self.session = request.session
        session_cart = self.session.get(settings.CART_SESSION_ID)
        if not session_cart:
            session_cart = self.session[settings.CART_SESSION_ID] = {}
        self.session_cart = session_cart

    def _save_cart(self):
        self.session.modified = True

    def get_cart_as_list(self):
        cart = []
        if not self.session_cart:
            return cart
        for offer_pk, amount in self.session_cart.items():
            record = UserOfferCART(offer_id=int(offer_pk), amount=amount)
            cart.append(record)
        return cart

    def remove_from_cart(self, offer_id: int):
        try:
            self.session_cart.pop(str(offer_id))
            self._save_cart()
        except KeyError:
            return

    def add_to_cart(self, offer_id: int, amount=1):
        current_amount = int(self.session_cart.get(str(offer_id), "0"))
        self.session_cart[str(offer_id)] = str(current_amount + amount)
        self._save_cart()

    def change_amount(self, offer_id: int, amount: int):
        if not self.session_cart.get(str(offer_id)):
            raise UserOfferCART.DoesNotExict("Такого предложения не найдено в корзине")
        self.session_cart[str(offer_id)] = str(amount)
        self._save_cart()

    def get_length(self):
        length = 0
        for amount in self.session_cart.values():
            length += int(amount)
        return length

    def clear(self):
        self.session_cart.clear()
        self._save_cart()


class UserCart:
    def __init__(self, request: HttpRequest):
        self.user = request.user

    def get_cart_as_list(self) -> list:
        return list(UserOfferCART.objects.filter(user=self.user).all())

    def remove_from_cart(self, offer_id: int):
        try:
            cart_record = UserOfferCART.objects.get(user=self.user, offer_id=offer_id)
            cart_record.delete()
        except UserOfferCART.DoesNotExist:
            return
        except UserOfferCART.MultipleObjectsReturned:
            cart_records = UserOfferCART.objects.filter(user=self.user, offer_id=offer_id)
            cart_records.delete()

    def add_to_cart(self, offer_id: int, amount=1):
        cart_record, created = UserOfferCART.objects.get_or_create(user=self.user, offer_id=offer_id)
        if not created:
            cart_record.amount += amount
            cart_record.save()
        else:
            if amount > 1:
                self.change_amount(offer_id, amount)

    def change_amount(self, offer_id: int, amount: int):
        cart_record = UserOfferCART.objects.get(user=self.user, offer_id=offer_id)
        cart_record.amount = amount
        cart_record.save()

    def get_length(self):
        length = UserOfferCART.objects.get(user=self.user).count("number")
        return length

    def clear(self):
        queryset = self.get_cart_or_none()
        queryset.delete()

    def _save_cart(self):
        pass


def _merge_session_cart(request: HttpRequest, anonim_cart: AnonimCart):
    user_cart = UserCart(request)
    session_cart_as_dict = anonim_cart.session_cart
    for offer_id, amount in session_cart_as_dict.items():
        user_cart.add_to_cart(int(offer_id), int(amount))
    return user_cart


def get_cart(request: HttpRequest) -> Union[UserCart, AnonimCart]:
    if request.user.is_anonymous:
        return AnonimCart(request)
    else:
        anonim_cart = AnonimCart(request)
        if not anonim_cart.session_cart:
            return UserCart(request)
        else:
            return _merge_session_cart(request, anonim_cart)
