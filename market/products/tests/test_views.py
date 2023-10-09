from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import render, reverse

import random

from products.models import Product, Category, Detail, Review, Manufacturer, Banner
from shops.models import Shop, Offer

from products.services.review_services import ReviewServices

FIXTURES = [
    "fixtures/01-users.json",
    "fixtures/02-groups.json",
    "fixtures/04-shops.json",
    "fixtures/05-category.json",
    "fixtures/06-manufacturer.json",
    "fixtures/07-tags.json",
    "fixtures/08-products.json",
    "fixtures/09-offers.json",
    "fixtures/10-details.json",
    "fixtures/11-productimages.json",
    "fixtures/12-productdetails.json",
    "fixtures/13-reviews.json",
    "fixtures/14-banners.json",
]

User = get_user_model()


class HomeViewTest(TestCase):
    fixtures = FIXTURES

    def test_example_view(self):
        template = "products/home-page.jinja2"
        request = HttpRequest()
        context = dict()
        context["offers"] = Offer.objects.order_by("?")[:8]
        context["min_price_product"] = Offer.objects.all().order_by("price").first()
        min_offers = []
        categories = Category.objects.filter(foreground=True).order_by("?")[:3]
        if len(categories) > 3:
            categories = random.choices(categories, k=3)
        for category in categories:
            min_product = Offer.objects.filter(product__pk=category.pk).order_by("price").first()
            min_offers.append(min_product)
        context["min_offers"] = min_offers
        context["limited_products"] = Offer.objects.all().order_by("remains")[:8]
        banners = Banner.objects.filter(archived=False).order_by("?")[:3]
        context["banners"] = banners
        response = render(request, template, context)
        self.assertEqual(response.status_code, 200)


class ProductViewTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.detail = Detail.objects.create(name="Тестовая характеристика")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.product = Product.objects.create(
            name="Тестовый продукт",
            category=cls.category,
            manufacturer=cls.manufacturer,
            preview="/img/products/test_product/",
        )
        cls.product.details.set([cls.detail], through_defaults={"value": "тестовое значение"})
        cls.user = User.objects.create(username="Test_user", email="test@test.com", password="Test123!$")
        cls.review = Review.objects.create(
            user=cls.user, product=cls.product, review_content="Тестовая отзыв продукта"
        )
        cls.shop = Shop.objects.create(user=cls.user, name="тестовый магазин")
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=25, remains=42)

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
