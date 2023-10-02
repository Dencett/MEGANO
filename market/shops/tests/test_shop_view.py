from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from products.models import Product, Category, Detail
from shops.models import Shop

User = get_user_model()


# class ShopDetailViewTestCase(TestCase):
#     @classmethod
#     def setUpClass(cls) -> None:
#         shop_info = dict(
#             ("name", "Test shop"),
#             ("about", "Test about"),
#         )


FIXTURES = [
    "fixtures/0 1-groups.json",
    "fixtures/0-01-users.json",
    "fixtures/0-04-shops.json",
    "fixtures/05-category.json",
    "fixtures/06-tags.json",
    "fixtures/07-products.json",
    "fixtures/08-offers.json",
    "fixtures/09-details.json",
    "fixtures/10-productimages.json",
    "fixtures/11-productdetails.json",
]


class ShopViewTestCase(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpClass(cls) -> None:
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.detail = Detail.objects.create(name="тестовая характеристика")
        cls.product = Product.objects.create(
            name="test product for shop",
            category=cls.category,
        )
        cls.product.details.set([cls.detail], through_defaults={"value": "тестовое значение"})

        cls.user = User.objects.create(
            username="test_user_for_shop_test",
            password="QWerty1234",
            email="test_user@mail.com",
        )

        cls.shop = Shop.objects.create(
            user=cls.user,
            name="Test shop 55",
            about="Test description test shop 123124312",
            phone="89006663322",
            email="test-shop-reatailer@mail.com",
            avatar="media/shops/1/avatar/dns.jpg",
        )
        cls.shop.products.set([cls.product], through_defaults={"price": "1235.99"})

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()
        cls.shop.delete()
        cls.product.delete()
        cls.detail.delete()
        cls.category.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_example_view(self):
        template = "shops/shop_detail.jinja2"
        response = self.client.get(reverse("shops:shop_detail", kwargs={"pk": self.shop.pk}))
        # request = HttpRequest()  # reverse("shops:shop_detail", kwargs={"pk": self.shop.pk}) # '/shops/1/'
        # context = {
        #     "shop": self.shop,
        #     "user": self.user,
        # }
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test-shop-reatailer@mail.com")
        self.assertEqual(response.template_name[0], template)

    def test_shop_products(self):
        response = self.client.get(reverse("shops:shop_products", kwargs={"pk": self.shop.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], "shops/shop_products.jinja2")
        self.assertContains(response, "test product for shop")

    def test_update_shop_information(self):
        response = self.client.get(reverse("shops:shop-update", kwargs={"pk": self.shop.pk}))
        self.assertEqual(response.status_code, 200)

    def test_shop_product_detail(self):
        response = self.client.get(reverse("products:product-detail", kwargs={"pk": self.shop.products.first().pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test product for shop")


class ShopModelTestCase(TestCase):
    """Класс тестов модели Магазин"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.detail = Detail.objects.create(name="тестовая характеристика")
        cls.product = Product.objects.create(
            name="test product for shop",
            category=cls.category,
        )
        cls.product.details.set([cls.detail], through_defaults={"value": "тестовое значение"})

        cls.user = User.objects.create(
            username="test_user_for_shop_test",
            password="QWerty1234",
            email="test_user@mail.com",
        )

        cls.shop = Shop.objects.create(
            user=cls.user,
            name="Test shop 55",
            about="Test description test shop 123124312",
            phone="89006663322",
            email="test-shop-reatailer@mail.com",
            avatar="media/shops/1/avatar/dns.jpg",
        )
        cls.shop.products.set([cls.product], through_defaults={"price": "1235.99"})

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()
        cls.shop.delete()
        cls.product.delete()
        cls.detail.delete()
        cls.category.delete()

    def test_verbose_name(self):
        shop = ShopModelTestCase.shop
        field_verboses = {
            "name": "название",
            "about": "Описание магазина",
            "phone": "Телефон магазина",
            "email": "Емаил магазина",
            "avatar": "Аватар",
            "products": "товары в магазине",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(shop._meta.get_field(field).verbose_name, expected_value)

    def test_check_the_database_for_compliance(self):
        # self.assertEqual(self.shop.pk, 1)
        self.assertEqual(self.shop.name, "Test shop 55")
        self.assertEqual(self.shop.email, "test-shop-reatailer@mail.com")
        self.assertEqual(self.shop.phone, "89006663322")
        self.assertEqual(self.shop.avatar, "media/shops/1/avatar/dns.jpg")
        self.assertEqual(self.shop.user.username, "test_user_for_shop_test")
        self.assertEqual(self.shop.user.email, "test_user@mail.com")


# name = "Test shop 55",
# about = "Test description test shop 123124312",
# phone = "89006663322",
# email = "test-shop-reatailer@mail.com",
# avatar = "media/shops/1/avatar/dns.jpg",
# # ===========================================
# class ProductModelTest(TestCase):
#     """Класс тестов модели Продукт"""
#
#     @classmethod
#     def setUpClass(cls):
#         cls.category = Category.objects.create(name="Тестовая категория")
#
#         cls.detail = Detail.objects.create(name="тестовая характеристика")
#         cls.product = Product.objects.create(
#             name="Тестовый продукт",
#             category=cls.category,
#         )
#         cls.product.details.set([cls.detail], through_defaults={"value": "тестовое значение"})
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.detail.delete()
#         cls.product.delete()
#         cls.category.delete()
#
#     def test_verbose_name(self):
#         product = ProductModelTest.product
#         field_verboses = {
#             "name": "наименование",
#             "details": "характеристики",
#         }
#         for field, expected_value in field_verboses.items():
#             with self.subTest(field=field):
#                 self.assertEqual(product._meta.get_field(field).verbose_name, expected_value)
#
#     def test_name_max_length(self):
#         product = ProductModelTest.product
#         max_length = product._meta.get_field("name").max_length
#         self.assertEqual(max_length, 512)
#
#     def test_productdetail_value(self):
#         productdetail = ProductDetail.objects.all()[0]
#         value = productdetail.value
#         self.assertEqual(value, "тестовое значение")
#
#     def test_product_fields_name(self):
#         attr_names = dir(Product())
#         variable_name_in_template = (
#             "shops",
#             "preview",
#             "productimage_set",
#             "name",
#             "about",
#             "tags",
#             "description",
#             "offer_set",
#             "productdetail_set",
#         )
#         for name in variable_name_in_template:
#             self.assertIn(name, attr_names)

# ===========================================
