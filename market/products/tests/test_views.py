from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import render

from products.services import category_menu
from products.models import Product

FIXTURES = [
    "fixtures/04-shops.json",
    "fixtures/05-category.json",
    "fixtures/06-tags.json",
    "fixtures/07-products.json",
    "fixtures/08-offers.json",
    "fixtures/09-details.json",
    "fixtures/10-productimages.json",
    "fixtures/11-productdetails.json",
]


class ExampleViewTest(TestCase):
    fixtures = FIXTURES

    def test_example_view(self):
        template = "base.jinja2"
        request = HttpRequest()
        context = {"menu": category_menu()}
        response = render(request, template, context)
        self.assertEqual(response.status_code, 200)


class ProductsViewTest(TestCase):
    fixtures = FIXTURES

    def test_products_detail_view(self):
        template = "products/product_details.jinja2"
        request = HttpRequest()
        product = Product.objects.get(pk=1)
        context = {"product": product}
        response = render(request, template, context)
        self.assertEqual(response.status_code, 200)
