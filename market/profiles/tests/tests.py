from django.test import TestCase
from django.urls import reverse

from profiles.models import User


class UserLogoutTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # создает пользователя
        cls.credentials = {
            "username": "bob_test",
            "email": "bob_test@mail.com",
            "password": "qwerty",
        }
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    def test_logout_user(self):
        response = self.client.get(reverse("profiles:logout"))
        to_reverse = self.client.get(reverse("profiles:home-page"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profiles:home-page"))
        self.assertEqual(to_reverse.status_code, 200)


class UserLoginTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_login_info = {
            "username": "John-test",
            "email": "jhon@test.com",
            "password": "JohnTest1234",
        }
        cls.user = User.objects.create(**cls.user_login_info)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(
            email=self.user_login_info["email"],
            password=self.user_login_info["password"],
        )

    def test_user_login(self):
        response = self.client.get(reverse("profiles:home-page"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Главная страница маркетплейса")
        # self.assertContains(response, self.user.username)

    def test_user_login_to_about_user_page(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.template_name)

    def test_user_login_to_change_password_page(self):
        response = self.client.get(reverse("profiles:change-password"))
        self.assertEqual(response.request["PATH_INFO"], "/profiles/change_password/")

    def test_user_login_to_register_page(self):
        response = self.client.get(reverse("profiles:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registration page")
        self.assertContains(response, "Выбрать, если вы хотите стать продавцом на сайте:")


class UserRegisterTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_info = {
            "username": "John-test",
            "phone": "89701112233",
            "residence": "London",
            "address": "Bakers streets 148 ap.3",
            "retailer_group": True,
        }
        cls.user_login_info = {
            "email": "jhon@test.com",
            "password": "JohnTest1234",
        }

        cls.user = User.objects.create_user(
            username=cls.all_info["username"],
            email=cls.user_login_info["email"],
            password=cls.user_login_info["password"],
            phone=cls.all_info["phone"],
            residence=cls.all_info["residence"],
            address=cls.all_info["address"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.user_login_info)

    def test_user_permissions_active(self):
        response = self.client.get(reverse("profiles:home-page"))
        self.assertEqual(response.status_code, 200)

    def test_register_user_sign_in_profile(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertEqual(response.status_code, 200)

    def test_register_user_sign_in_change_password(self):
        response = self.client.get(reverse("profiles:change-password"))
        self.assertEqual(response.status_code, 200)

    def test_register_user_sign_in_logout(self):
        response = self.client.get(reverse("profiles:logout"))
        to_home = self.client.get(reverse("profiles:home-page"))
        url = to_home.wsgi_request.META["PATH_INFO"]
        self.assertEqual(response.url, url)


class UserChangeInformationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.create = {
            "username": "Jhon-test",
            "email": "jhon_test@gmail.com",
            "password": "qwerty1234",
            "phone": "89991112233",
            "residence": "Test residence",
            "address": "California one apple park 1",
            "avatar": "",
        }
        cls.user = User.objects.create_user(**cls.create)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(email=self.create["email"], password=self.create["password"])

    def test_user_login(self):
        response = self.client.get(reverse("profiles:home-page"))
        self.assertEqual(response.status_code, 200)

    def test_user_get_about_user_page(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "Страница детальной информации")
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.address)
        self.assertContains(response, self.user.residence)
