from django.test import TestCase  # noqa
from django.urls import reverse
from django.contrib.auth import get_user_model

from catalog.tests.utils import get_fixtures_list, echo_sql
from orders.models import Order


User = get_user_model()


class OrderCreateTestCase(TestCase):
    """Тест создания заказа"""

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

        self.client.login(email="test_user@mail.com", password="qwerty1234")

    def tearDown(self) -> None:
        self.user.delete()
        self.order.delete()

    @echo_sql
    def test_create_order(self):
        order = Order.objects.last()
        self.assertEqual(self.order.order_number, 1)
        self.assertEqual(self.order.user.username, "test_user")
        self.assertEqual(self.order.payment_type, "картой")
        self.assertEqual(self.order.payment_type, order.payment_type)


class UserHistoryOrdersListViewTestCase(TestCase):
    """Тест истории заказов пользователя"""

    fixtures = get_fixtures_list()

    @classmethod
    def setUpClass(cls):
        cls.all_info = {
            "username": "John-test",
            "phone": "89701112233",
            "residence": "London",
            "address": "Bakers streets 148 ap.3",
            "retailer_group": True,
        }
        cls.user_login_info = {
            "email": "jhon@test.com",
            "password": "JohnTest1234",
        }

        cls.user = User.objects.create_user(
            username=cls.all_info["username"],
            email=cls.user_login_info["email"],
            password=cls.user_login_info["password"],
            phone=cls.all_info["phone"],
            residence=cls.all_info["residence"],
            address=cls.all_info["address"],
        )

        cls.order_data = {
            "user": cls.user,
            "city": "test city",
            "address": "test address",
            "delivery_type": "usually",
            "payment_type": "card",
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
        self.client.login(**self.user_login_info)

    # @echo_sql
    def test_order_contains_delivery_type(self):
        response = self.client.get(reverse("orders:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "обычная доставка")

    def test_contains_payment_type(self):
        response = self.client.get(reverse("orders:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Картой")

    def test_contains_order_number(self):
        response = self.client.get(reverse("orders:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)
