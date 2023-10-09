from django.test import TestCase

from django.test.client import RequestFactory

from django.conf import settings
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from importlib import import_module
from django.contrib.auth import login

from catalog.tests.utils import get_fixtures_list
from profiles.models import User
from shops.models import Offer
from ..services import cart_service
from ..models import UserOfferCart


def get_user(request):
    if not hasattr(request, "_cached_user"):
        request._cached_user = auth.get_user(request)
    return request._cached_user


def middleware(request):
    engine = import_module(settings.SESSION_ENGINE)
    SessionStore = engine.SessionStore
    session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
    request.session = SessionStore(session_key)
    request.user = SimpleLazyObject(lambda: get_user(request))
    return request


class UserCartServiceTest(TestCase):
    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(pk=1)
        UserOfferCart.objects.filter(user=cls.user).delete()
        # cls.middleware = SessionMiddleware.process_request()
        # cls.auth_middleware = AuthenticationMiddleware.process_request

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = middleware(self.factory.request())
        login(self.request, self.user)

    def tearDown(self) -> None:
        UserOfferCart.objects.filter(user=self.user).delete()

    def test_model_test(self):
        offer = Offer.objects.get(pk=4)
        number = 4
        UserOfferCart(user=self.user, offer=offer, amount=number).save()
        cart_record = UserOfferCart.objects.get(user=self.user, offer=offer)
        amount = cart_record.amount
        self.assertEqual(amount, number)

    def test_get_UserCart(self):
        offer = Offer.objects.get(pk=2)
        number = 3
        record = UserOfferCart(user=self.user, offer=offer, amount=number)
        record.save()
        request = self.factory.request()
        middleware(request)
        login(request, self.user)
        cart = cart_service.get_cart(request)
        cartlist = cart.get_cart_as_list()
        self.assertIn(record, cartlist)

    def test_add_UserCart(self):
        request = self.factory.request()
        middleware(request)
        login(request, self.user)
        cart = cart_service.get_cart(request)
        offer_id = 4
        amount = 2
        cart.add_to_cart(offer_id, amount=amount)
        record = UserOfferCart.objects.get(user=self.user, offer_id=offer_id)
        self.assertEqual(record.amount, amount)

    def test_re_add_UserCart(self):
        request = self.factory.request()
        middleware(request)
        login(request, self.user)
        cart = cart_service.get_cart(request)
        offer_id = 4
        amount = 2
        UserOfferCart(user=self.user, offer_id=offer_id, amount=amount).save()
        cart.add_to_cart(offer_id, amount=amount)
        record = UserOfferCart.objects.get(user=self.user, offer_id=offer_id)
        self.assertEqual(record.amount, amount * 2)

    def test_delete_UserCart(self):
        request = self.request
        cart = cart_service.get_cart(request)
        offer_id = 4
        amount = 2
        UserOfferCart(user=self.user, offer_id=offer_id, amount=amount).save()
        cart.remove_from_cart(offer_id=4)
        with self.assertRaises(UserOfferCart.DoesNotExist):
            UserOfferCart.objects.get(user=self.user, offer_id=offer_id)

    def test_clear_UserCart(self):
        request = self.request
        cart = cart_service.get_cart(request)
        offer_id = 4
        amount = 2
        UserOfferCart(user=self.user, offer_id=offer_id, amount=amount).save()
        UserOfferCart(user=self.user, offer_id=5, amount=amount).save()
        UserOfferCart(user=self.user, offer_id=3, amount=amount).save()
        cart.clear()
        queryset = UserOfferCart.objects.filter()
        self.assertFalse(queryset)


class AnonimCartServiceTest(TestCase):
    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = middleware(self.factory.request())

    def test_get_AnonimCart(self):
        cart = cart_service.get_cart(self.request)
        self.assertIsInstance(cart, cart_service.AnonimCart)

    def test_get_AnonimCart_authenticated_user(self):
        user = User.objects.get(pk=1)
        login(self.request, user)
        cart = cart_service.get_cart(self.request)
        self.assertNotIsInstance(cart, cart_service.AnonimCart)

    def test_add_AnonimCart(self):
        cart = cart_service.get_cart(self.request)
        offer = Offer.objects.get(pk=2)
        cart.add_to_cart(offer.pk)
        session_cart = self.request.session["cart"]
        expected_amount = 1
        expected_cart = {str(offer.pk): str(expected_amount)}
        self.assertDictEqual(session_cart, expected_cart)

    def test_re_add_AnonimCart(self):
        cart = cart_service.get_cart(self.request)
        offer = Offer.objects.get(pk=2)
        cart.add_to_cart(offer.pk, 1)
        amount = "5"
        cart.add_to_cart(offer.pk, amount)
        session_cart = self.request.session["cart"]
        expected_amount = 6
        expected_cart = {str(offer.pk): str(expected_amount)}
        self.assertDictEqual(session_cart, expected_cart)

    def test_add_one_more_offer_AnonimCart(self):
        cart = cart_service.get_cart(self.request)
        offer_list = [Offer.objects.get(pk=i) for i in range(1, 15, 5)]
        for offer in offer_list:
            cart.add_to_cart(offer.pk)
        session_cart = self.request.session["cart"]
        expected_cart = {str(offer.pk): str(1) for offer in offer_list}
        self.assertDictEqual(session_cart, expected_cart)

    def test_delete_offer_AnonimCart(self):
        self.request.session["cart"] = {"10": "5", "1": "3"}
        cart = cart_service.get_cart(self.request)
        cart.remove_from_cart(10)
        session_cart = self.request.session["cart"]
        expected_cart = {"1": "3"}
        self.assertDictEqual(session_cart, expected_cart)

    def test_clear_AnonimCart(self):
        self.request.session["cart"] = {"10": "5", "1": "3"}
        cart = cart_service.get_cart(self.request)
        cart.clear()
        session_cart = self.request.session["cart"]
        expected_cart = {}
        self.assertDictEqual(session_cart, expected_cart)

    def test_session_cart_size(self):
        cart = cart_service.get_cart(self.request)
        cart.add_to_cart(5, 5)
        cart.add_to_cart(3, 1)
        cart_size = self.request.session["cart_size"]
        expected_cart_size = "6"
        self.assertEqual(cart_size, expected_cart_size)

    def test_clear_cart_size(self):
        self.request.session["cart"] = {"10": "5", "1": "3"}
        cart = cart_service.get_cart(self.request)
        cart.clear()
        cart_size = self.request.session["cart_size"]
        expected_cart_size = "0"
        self.assertEqual(cart_size, expected_cart_size)


class MergeAnonimAndUserCartServiceTest(TestCase):
    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(pk=1)
        UserOfferCart.objects.filter(user=cls.user).delete()

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = middleware(self.factory.request())

    def test_merge_anonim_and_user_cart(self):
        self.request.session["cart"] = {"10": "5", "1": "3"}
        self.request.session["cart_size"] = "8"
        UserOfferCart(offer_id=2, user=self.user, amount=3).save()
        UserOfferCart(offer_id=12, user=self.user, amount=1).save()
        login(self.request, self.user)
        cart_service.login_cart(self.request)

        queryset = UserOfferCart.objects.filter(user=self.user).select_related("offer")
        offer_id_set = {record.offer.id for record in queryset}
        expected_offer_id_set = {10, 1, 2, 12}
        self.assertSetEqual(offer_id_set, expected_offer_id_set)

        cart_size = self.request.session["cart_size"]
        expected_cart_size = "12"
        self.assertEqual(cart_size, expected_cart_size)
