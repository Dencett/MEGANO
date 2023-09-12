from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import render

from products.services import category_menu
from products.models import Product


class ExampleViewTest(TestCase):
    fixtures = [
        "fixtures/02-shops.json",
        "fixtures/04-tags.json",
        "fixtures/05-category.json",
        "fixtures/06-products.json",
        "fixtures/07-offers.json",
        "fixtures/09-details.json",
        "fixtures/10-productimages.json",
        "fixtures/11-productdetails.json",
    ]

    def test_example_view(self):
        template = "base.jinja2"
        request = HttpRequest()
        context = {"menu": category_menu()}
        response = render(request, template, context)
        self.assertEqual(response.status_code, 200)


class ProductsViewTest(TestCase):
    fixtures = [
        "fixtures/02-shops.json",
        "fixtures/04-tags.json",
        "fixtures/05-category.json",
        "fixtures/06-products.json",
        "fixtures/07-offers.json",
        "fixtures/09-details.json",
        "fixtures/10-productimages.json",
        "fixtures/11-productdetails.json",
    ]

    def test_products_detail_view(self):
        template = "products/product_details.jinja2"
        request = HttpRequest()
        product = Product.objects.get(pk=1)
        context = {"product": product}
        response = render(request, template, context)
        self.assertEqual(response.status_code, 200)
