from django.test import TestCase
from profiles.models import User
from products.models import Product
from django.urls import reverse

FIXTURES = [
    "fixtures/01-users.json",
    "fixtures/04-shops.json",
    "fixtures/05-category.json",
    "fixtures/06-manufacturer.json",
    "fixtures/07-tags.json",
    "fixtures/08-products.json",
    "fixtures/09-offers.json",
    "fixtures/10-details.json",
    "fixtures/11-productimages.json",
    "fixtures/12-productdetails.json",
]


class UserHistoryViewTest(TestCase):
    """Класс тестов для записей в истории посещения пользователя"""

    fixtures = FIXTURES

    def setUp(self) -> None:
        user = User.objects.all().first()
        self.client.force_login(user)

    def test_permissions(self):
        self.client.logout()
        response = self.client.get(reverse("profiles:browsing_history"))
        status = response.status_code
        self.assertEqual(status, 302)

    def test_status_login_user(self):
        response = self.client.get(reverse("profiles:browsing_history"))
        status = response.status_code
        self.assertEqual(status, 200)

    def test_history(self):
        products = []
        for pk in range(1, 8):
            self.client.get(reverse("products:product-detail", kwargs={"pk": pk}))
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:browsing_history"))
        self.assertContains(response, products[2].name)

    def test_overwrite_history(self):
        products = []
        history_length = 9
        for pk in range(1, history_length + 1 + 2):
            self.client.get(reverse("products:product-detail", kwargs={"pk": pk}))
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:browsing_history"))
        self.assertNotContains(response, products[1].name)

    def test_last_record_history(self):
        products = []
        history_length = 9
        for pk in range(1, history_length + 1 + 2):
            self.client.get(reverse("products:product-detail", kwargs={"pk": pk}))
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:browsing_history"))
        self.assertContains(response, products[-1].name)


class AboutUserViewTest(TestCase):
    fixtures = FIXTURES

    def setUp(self) -> None:
        user = User.objects.all().first()
        self.client.force_login(user)

    def test_history(self):
        products = []
        for pk in range(1, 4):
            self.client.get(reverse("products:product-detail", kwargs={"pk": pk}))
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:about-user"))
        self.assertContains(response, products[2].name)

    def test_over_history(self):
        products = []
        for pk in range(1, 8):
            self.client.get(reverse("products:product-detail", kwargs={"pk": pk}))
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:about-user"))
        self.assertNotContains(response, products[2].name)

    def test_last_product_in_history(self):
        products = []
        for pk in range(1, 8):
            self.client.get(reverse("products:product-detail", kwargs={"pk": pk}))
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:about-user"))
        self.assertContains(response, products[-1].name)

    def test_null_history(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertNotContains(response, "Вы смотрели")

    def test_some_history(self):
        self.client.get(reverse("products:product-detail", kwargs={"pk": 1}))
        response = self.client.get(reverse("profiles:about-user"))
        self.assertContains(response, "Вы смотрели")
