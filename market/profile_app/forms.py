from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import BaseUserCreationForm, UsernameField


class UserRegisterForm(BaseUserCreationForm):
    """
    Форма регистрации пользователя. Запрашивает все необходимые данные.
    Запрашивает у пользователя, хочет ли он стать продавцом на сайте или нет.
    """

    phone_number = forms.CharField(label="Номер телефона", max_length=11, help_text="Вводите номер через '8'")
    residence = forms.CharField(max_length=80, label="Город проживания")
    address = forms.CharField(
        max_length=80,
        label="Адрес доставки",
        widget=forms.Textarea(attrs={"cols": "60", "rows": "5"}),
    )

    retailer_group = forms.BooleanField(
        initial=False,
        required=False,
        label="Выбрать, если вы хотите стать продавцом на сайте",
    )
    error_messages = {
        "password_mismatch": "Два пароля не совпали.",
    }
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "новый пароль"}),
        # help_text=password_validation.password_validators_help_text_html(),
        help_text="<ul><li>Ваш пароль не должен быть слишком похож на другую "
        "вашу личную информацию.</li>"
        "<li>Ваш пароль должен содержать не менее 8 символов.</li>"
        "<li>Ваш пароль не может быть часто используемым паролем.</li>"
        "<li>Ваш пароль не может быть полностью цифровым.</li></ul>",
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"autocomplete": "новый пароль"}),
        strip=False,
        help_text="Введите тот же пароль, что и раньше, для проверки.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "residence",
            "address",
            "retailer_group",
        ]  # "__all__",

        field_classes = {
            "username": UsernameField,
            "first_name": forms.CharField,
            "last_name": forms.CharField,
            "email": forms.EmailField,
            "password1": forms.CharField,
            "phone_number": forms.CharField,
            "residence": forms.CharField,
            "address": forms.CharField,
            "retailer_group": forms.BooleanField,
        }


class ProfileAvatarUpdateForm(forms.Form):
    user_avatar = forms.ImageField()
