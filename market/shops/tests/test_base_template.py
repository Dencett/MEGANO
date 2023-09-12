from django.test import TestCase
from django.shortcuts import render
from django.http.request import HttpRequest


class BaseTemplateTest(TestCase):
    def test_template_render(self):
        template = "base.jinja2"
        request = HttpRequest()
        # context = {'menu': category_menu()}
        context = {}
        response = render(request, template, context=context)
        status = response.status_code
        self.assertEqual(status, 200)
