from django.test import TestCase  # noqa
from django.urls import reverse
from orders.models import Order
from profiles.models import User
from shops.models import Offer


class OrderDetailTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            email="test_user@mail.com",
            username="test_user",
            password="qwerty1234",
        )
        order_data = {
            "user": self.user,
            "city": "test city",
            "address": "test address",
            "delivery_type": "Новый заказ",
            "payment_type": "картой",
            # "order_number": ,
            "status": "created",
        }
        self.order = Order.objects.create(**order_data)
        self.product = Offer.objects.get(pk=14)

        self.client.login(email=self.user["email"], password=self.user["password"])

    def tearDown(self) -> None:
        self.user.delete()
        self.user.delete()
        self.user.delete()

    def test_details(self):
        pass


class OrderCreateTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            email="test_user@mail.com",
            username="test_user",
            password="qwerty1234",
        )

        some_data = {
            "user": self.user,
            "city": "test city",
            "address": "test address",
            "delivery_type": "Новый заказ",
            "payment_type": "картой",
            # "order_number": ,
            "status": "created",
        }
        self.order = Order.objects.create(**some_data)

    def tearDown(self) -> None:
        self.user.delete()
        self.order.delete()

    def test_create_order(self):
        self.assertEqual(self.order.order_number, 1)
        self.assertEqual(self.order.user.username, "test_user")


class UserHistoryOrdersListViewTestCase(TestCase):
    """Тест истории заказов пользователя"""

    @classmethod
    def setUpClass(cls):
        cls.credentials = {"username": "test_user", "password": "qwerty", "email": "test_user@mail.com"}
        # Создание пользователя
        cls.user = User.objects.create_user(**cls.credentials)

        cls.order_data = {
            "user": cls.user,
            "city": "test city",
            "address": "test address",
            "delivery_type": "Новый заказ",
            "payment_type": "картой",
            # "order_number": ,
            "status": "created",
        }
        # Создание заказа
        cls.order = Order.objects.create(**cls.order_data)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()  # Удалить пользователя после теста
        cls.order.delete()  # Удалить заказ после теста

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    def test_order_list(self):
        # response = self.client.get(reverse("profiles:logout"))
        response = self.client.get(reverse("orders:history"))
        self.assertEqual(response.status_code, 200)


# @classmethod
# def setUpTestData(cls):
#     # создает пользователя
#     cls.credentials = {"username": "bob_test", "password": "qwerty"}
#     cls.user = User.objects.create_user(**cls.credentials)
#
# def setUp(self) -> None:
#     self.client.login(**self.credentials)
