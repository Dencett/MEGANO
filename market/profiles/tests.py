from django.test import TestCase
from django.urls import reverse

from .models import Profile, User


class UserLogoutTestCase(TestCase):
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


class UserLoginTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_login_info = {
            "username": "John-test",
            "email": "jhon@test.com",
            "password": "JohnTest1234",
        }
        cls.profile_info = {
            "phone_number": "89701112233",
            "residence": "London",
            "address": "Bakers streets 148 ap.3",
        }
        cls.user = User.objects.create_user(**cls.user_login_info)
        cls.profile = Profile.objects.create(
            user=cls.user,
            phone_number=cls.profile_info["phone_number"],
            residence=cls.profile_info["residence"],
            address=cls.profile_info["address"],
        )

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
        self.assertTrue("Главная страница маркетплейса")
        self.assertContains(response, self.user.username)

    def test_user_login_to_about_user_page(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About user information")
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


class UserRegisterTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_info = {
            "username": "John-test",
            "phone_number": "89701112233",
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
        )
        cls.profile = Profile.objects.create(
            user=cls.user,
            phone_number=cls.all_info["phone_number"],
            residence=cls.all_info["residence"],
            address=cls.all_info["address"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.profile.delete()

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
