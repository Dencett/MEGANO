from django import forms


class CleanNoneValuesFromMixin:
    def clean(self):
        """
        Remove: None, False, empty string in cleaned_data.
        """

        cleaned_data = super().clean()  # type: ignore
        return {key: value for key, value in cleaned_data.items() if value}


class CatalogFilterForm(CleanNoneValuesFromMixin, forms.Form):
    search = forms.CharField(max_length=256)

    price = forms.CharField(max_length=20)
    title = forms.CharField(max_length=256)
    remains = forms.BooleanField(required=False)
    free_delivery = forms.BooleanField(required=False)
