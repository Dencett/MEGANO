from django import forms


class CatalogFilterForm(forms.Form):
    price = forms.CharField(max_length=20)
    title = forms.CharField(max_length=256)
    remains = forms.BooleanField(required=False)
    free_delivery = forms.BooleanField(required=False)

    def clean(self):
        """
        Remove: None, False, empty string in cleaned_data.
        """

        cleaned_data = super().clean()
        return {key: value for key, value in cleaned_data.items() if value}
