from django import forms


class UserOneOfferCARTForm(forms.Form):
    """Форма"""

    amount = forms.IntegerField(min_value=0)
    offer_id = forms.IntegerField()


class UserManyOffersCARTForm(forms.Form):
    """Форма"""

    def __init__(self, number: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(number):
            self.fields["amount_i"] = forms.IntegerField(min_value=0)
            self.fields["offer_id_i"] = forms.IntegerField()
