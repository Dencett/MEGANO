from django import forms
from django.forms.widgets import HiddenInput

from cart.models import UserOfferCart


class UserOneOfferCARTForm(forms.Form):
    """Форма для добавления одной записи в корзину"""

    amount = forms.IntegerField(min_value=0)
    offer_id = forms.IntegerField()


class UserManyOffersCARTForm(forms.Form):
    """
    Форма для множественного добавления записей в корзину
    при этом поля должны содержать:
    offer_id[i]
    amount[i]
    """

    def __init__(self, number: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(number):
            self.fields[f"amount[{i}]"] = forms.IntegerField(min_value=0)
            self.fields[f"offer_id[{i}]"] = forms.IntegerField()


class UserOneOfferCARTDeleteForm(forms.Form):
    """Форма для удаления"""

    offer_id = forms.IntegerField(min_value=0, widget=HiddenInput())


class NewForm(forms.ModelForm):
    class Meta:
        model = UserOfferCart
        fields = (
            "offer",
            "amount",
        )
