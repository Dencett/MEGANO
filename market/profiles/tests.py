from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class LogoutViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # создает пользователя
        cls.credentials = {"username": "bob_test", "password": "qwerty"}
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


class UserRegisterTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_login_info = {
            "username": "John-test",
            "password": "JohnTest1234",
        }
        cls.user_info = {
            "first_name": "John",
            "last_name": "JohnJunior",
            "email": "test@test.com",
            "phone_number": "89998881122",
            "residence": "89998881122",
            "address": "Tagil",
        }
        cls.user = User.objects.create_user(**cls.user_login_info)

        cls.user_profile = Profile(
            user=cls.user,
            phone_number=cls.user_info["phone_number"],
            residence=cls.user_info["residence"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.user_info)

    def test_user_permissions_active(self):
        # self.user.groups.add("retailer")
        response = self.client.get("localhost:8000/admin/")
        self.assertEqual(response.status_code, 404)


class UserLoginTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_login_info = {
            "username": "John-test",
            "password": "JohnTest1234",
        }
        cls.user = User.objects.create_user(**cls.user_login_info)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.user_login_info)

    def test_user_login(self):
        response = self.client.get(reverse("profiles:home-page"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Главная страница маркетплейса")
        self.assertContains(response, self.user.username)

    def test_user_login_to_about_user_page(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Личный кабинет пользователя")
        self.assertContains(response, self.user.username)

    def test_user_login_to_change_password_page(self):
        response = self.client.get(reverse("profiles:change-password"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password change page")
        self.assertContains(response, "Old password:")

    def test_user_login_to_register_page(self):
        response = self.client.get(reverse("profiles:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registration page")
        self.assertContains(response, "Выбрать, если вы хотите стать продавцом на сайте:")
