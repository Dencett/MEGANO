from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import render, reverse

from products.models import Product, Category, Detail, Review
from shops.models import Shop, Offer

from products.services.review_services import ReviewServices

FIXTURES = [
    "fixtures/01-users.json",
    "fixtures/02-groups.json",
    "fixtures/04-shops.json",
    "fixtures/05-category.json",
    "fixtures/06-tags.json",
    "fixtures/07-products.json",
    "fixtures/08-offers.json",
    "fixtures/09-details.json",
    "fixtures/10-productimages.json",
    "fixtures/11-productdetails.json",
]


User = get_user_model()


class HomeViewTest(TestCase):
    fixtures = FIXTURES

    def test_example_view(self):
        template = "base.jinja2"
        request = HttpRequest()
        context = {}
        response = render(request, template, context)
        self.assertEqual(response.status_code, 200)


class ProductViewTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpClass(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.detail = Detail.objects.create(name="Тестовая характеристика")
        cls.product = Product.objects.create(
            name="Тестовый продукт", category=cls.category, preview="/img/products/test_product/"
        )
        cls.product.details.set([cls.detail], through_defaults={"value": "тестовое значение"})
        cls.user = User.objects.create(username="Test_user", email="test@test.com", password="Test123!$")
        cls.review = Review.objects.create(
            user=cls.user, product=cls.product, review_content="Тестовая отзыв продукта"
        )
        cls.shop = Shop.objects.create(user=cls.user, name="тестовый магазин")
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=25)

    @classmethod
    def tearDownClass(cls):
        cls.offer.delete()
        cls.shop.delete()
        cls.review.delete()
        cls.user.delete()
        cls.product.delete()
        cls.detail.delete()
        cls.category.delete()

    def test_product_detail_view(self):
        template = "products/product_details.jinja2"
        request = HttpRequest()
        review = ReviewServices(request=request, product=self.product)
        context = dict()

        context["product"] = self.product
        context["reviews"] = review.get_reviews()
        context["page_obj"] = review.listing(context["reviews"])

        response = render(request, template, context)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("products:product-detail", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/product/{pk}/".format(pk=self.product.pk))
        self.assertEqual(response.status_code, 200)

    def test_view_success_url_redirect(self):
        login = self.client.force_login(self.user)  # noqa F401
        response = self.client.post(
            reverse("products:product-detail", kwargs={"pk": self.product.pk}), {"review_content": "Test content"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url=reverse("products:product-detail", kwargs={"pk": self.product.pk}))
