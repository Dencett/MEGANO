from django.test import TestCase
from django.urls import reverse

from catalog.tests.utils import get_fixtures_list
from profiles.models import User
from shops.models import Offer
from ..models import UserOfferCart


class CartViewTest(TestCase):
    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(pk=1)
        UserOfferCart.objects.filter(user=cls.user).delete()

    def setUp(self):
        pass

    # def test_auth_CartView_test(self):
    #     offer_pk = 3
    #     UserOfferCart(user=self.user, offer_id=offer_pk, amount=5).save()
    #     offer = Offer.objects.get(pk=offer_pk)
    #     self.client.force_login(self.user)
    #     response = self.client.get(reverse("cart:user_cart"))
    #     self.assertContains(response, offer.product.name)

    def test_anon_CartView_test(self):
        self.client.logout()
        offer_pk = 3
        offer = Offer.objects.get(pk=offer_pk)
        session = self.client.session
        session["cart"] = {str(offer_pk): "5"}
        session.save()
        response = self.client.get(reverse("cart:user_cart"))
        self.assertContains(response, offer.product.name)
