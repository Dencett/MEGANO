from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import render


class ExampleViewTest(TestCase):
    def test_example_view(self):
        template = "base.jinja2"
        request = HttpRequest()
        context = {}
        response = render(request, template, context)
        self.assertEqual(response.status_code, 200)
