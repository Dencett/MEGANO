from django.test import TestCase
from products.models import Product, Detail, ProductDetail


class ProductModelTest(TestCase):
    """Класс тестов модели Продукт"""

    @classmethod
    def setUpClass(cls):
        cls.detail = Detail.objects.create(name="тестовая характеристика")
        cls.product = Product.objects.create(
            name="Тестовый продукт",
        )
        cls.product.details.set([cls.detail])

    @classmethod
    def tearDownClass(cls):
        cls.detail.delete()
        cls.product.delete()

    def test_verbose_name(self):
        product = ProductModelTest.product
        field_verboses = {
            "name": "наименование",
            "details": "характеристики",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(product._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        product = ProductModelTest.product
        max_length = product._meta.get_field("name").max_length
        self.assertEqual(max_length, 512)


class DetailModelTest(TestCase):
    """Класс тестов модели Свойство продукта"""

    @classmethod
    def setUpClass(cls):
        cls.detail = Detail.objects.create(name="тестовая характеристика")

    @classmethod
    def tearDownClass(cls):
        cls.detail.delete()

    def test_verbose_name(self):
        detail = DetailModelTest.detail
        field_verboses = {
            "name": "наименование",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(detail._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        detail = DetailModelTest.detail
        max_length = detail._meta.get_field("name").max_length
        self.assertEqual(max_length, 512)


class ProductDetailModelTest(TestCase):
    """Класс тестов модели Значение свойства продукта"""

    @classmethod
    def setUpClass(cls):
        cls.detail = Detail.objects.create(name="тестовая характеристика")
        cls.product = Product.objects.create(
            name="Тестовый продукт",
        )
        cls.product_detail = ProductDetail.objects.create(
            product=cls.product,
            detail=cls.detail,
            value="тестовое значение характеристики",
        )

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()
        cls.detail.delete()
        cls.product_detail.delete()

    def test_verbose_name(self):
        product_detail = ProductDetailModelTest.product_detail
        field_verboses = {
            "value": "значение",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(product_detail._meta.get_field(field).verbose_name, expected_value)

    def test_value_max_length(self):
        product_detail = ProductDetailModelTest.product_detail
        max_length = product_detail._meta.get_field("value").max_length
        self.assertEqual(max_length, 128)
