from django.test import TestCase
from profiles.models import UserProductHistory, User
from products.models import Product
from profiles.services import products_history

FIXTURES = [
    "fixtures/0-contenttypes.json",
    "fixtures/00-groups_and_permissions.json",
    "fixtures/01-users.json",
    "fixtures/04-shops.json",
    "fixtures/05-category.json",
    "fixtures/06-tags.json",
    "fixtures/07-products.json",
    "fixtures/08-offers.json",
    "fixtures/09-details.json",
    "fixtures/10-productimages.json",
    "fixtures/11-productdetails.json",
]


class ProductHistoryServiceTest(TestCase):
    """Класс тестов для записей в истории посещения пользователя"""

    fixtures = FIXTURES

    def setUp(self) -> None:
        self.user = User.objects.all().last()
        self.products = Product.objects.all()
        self.test_range = 12
        for i in range(self.test_range):
            products_history.make_record_in_history(self.user, product=self.products[i])

    def test_add_product_to_history(self):
        user = User.objects.all().first()
        test_range = 3
        for i in range(test_range):
            products_history.make_record_in_history(user, product=self.products[i])
        records_count = UserProductHistory.objects.filter(user=user).count()
        self.assertEqual(records_count, test_range)

    def test_add_overlow_record(self):
        records_count = UserProductHistory.objects.filter(user=self.user).count()
        expected_result = 9
        self.assertEqual(records_count, expected_result)

    def test_get_history(self):
        history = products_history.get_products_in_user_history(self.user)
        expected_result = 9
        self.assertEqual(len(history), expected_result)

    def test_last_product_in_history(self):
        history = products_history.get_products_in_user_history(self.user)
        expected_product = self.products[self.test_range - 9]
        self.assertIn(expected_product, history)

    def test_add_overwriting_record(self):
        strikeout_product = self.products[self.test_range - 10]
        history = products_history.get_products_in_user_history(self.user)
        self.assertNotIn(strikeout_product, history)

    def test_exists_add_product_record(self):
        product_exists_in_history = self.products[8]
        products_history.make_record_in_history(self.user, product=product_exists_in_history)
        history = products_history.get_products_in_user_history(self.user)
        self.assertEqual(product_exists_in_history, history[0])

    def test_get_some_history(self):
        test_number = 5
        history = products_history.get_products_in_user_history(self.user, test_number)
        self.assertEqual(len(history), test_number)

    def test_get_some_history_latest_records(self):
        test_number = 5
        history = products_history.get_products_in_user_history(self.user, test_number)
        expected_product = self.products[self.test_range - test_number]
        self.assertIn(expected_product, history)
