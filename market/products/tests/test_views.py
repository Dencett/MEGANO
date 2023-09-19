from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import render


from products.models import Product

from products.services.review_services import ReviewServices

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

    def test_product_detail_view(self):
        template = "products/product_details.jinja2"
        request = HttpRequest()
        product = Product.objects.get(pk=1)
        review = ReviewServices(request=request, product=product)
        context = dict()

        context["product"] = product
        context["reviews"] = review.get_reviews()
        context["page_obj"] = review.listing(context["reviews"])
        response = render(request, template, context)
        self.assertEqual(response.status_code, 200)

    def test_product_form_view(self):
        # в процессе
        pass
