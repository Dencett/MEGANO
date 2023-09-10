from django.contrib.auth.models import Group
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView, CreateView

from .models import Profile
from .forms import UserRegisterForm, ProfileAvatarUpdateForm


class AboutUserView(TemplateView):
    """View class заглушка - информация о пользователе."""

    # template_name = "profiles/about-user.html"
    template_name = "profiles/about-user.jinja2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_avatar"] = ProfileAvatarUpdateForm()
        return context

    def post(self, request):
        update_avatar = ProfileAvatarUpdateForm(request.POST, request.FILES)

        if update_avatar.is_valid():
            picture = update_avatar.cleaned_data.get("user_avatar")
            profile = Profile.objects.get(user=request.user)
            profile.avatar = picture
            profile.save()
            return HttpResponseRedirect(reverse("profiles:about-user"))
        return HttpResponseRedirect(reverse("profiles:about-user"))


class HomePage(TemplateView):
    """View class заглушка - главная страница сайта."""

    # template_name = "profiles/index.html"
    template_name = "profiles/index.jinja2"


class UserRegisterView(CreateView):
    """
    View class для регистрации пользователей. Если данные из формы валидны,
    авторизовывает пользователя и перенаправляет на главную страницу сайта.
    """

    form_class = UserRegisterForm
    # template_name = "profiles/register.html"
    template_name = "profiles/register.jinja2"
    success_url = reverse_lazy("profiles:home-page")

    def get(self, request, **kwargs):
        form = UserRegisterForm()
        super().get(form)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def form_valid(self, form):
        response = super().form_valid(form)

        password = form.cleaned_data.get("password1")
        email = form.cleaned_data.get("email")
        phone_number = form.cleaned_data.get("phone_number")
        residence = form.cleaned_data.get("residence")
        address = form.cleaned_data.get("address")
        retailer_group = form.cleaned_data.get("retailer_group")

        Profile.objects.create(
            user=self.object,
            phone_number=phone_number,
            residence=residence,
            address=address,
        )
        user = authenticate(
            self.request,
            email=email,
            password=password,
        )

        if retailer_group:
            group = Group.objects.get(name="retailer")
            if not user.is_staff:
                user.is_staff = True
            user.groups.add(group)
            user.save()
        login(request=self.request, user=user)
        return response


class UserLogoutView(LogoutView):
    """View class заглушка - user logout."""

    next_page = reverse_lazy("profiles:home-page")


class UserResetPasswordView(PasswordChangeView):
    """View class change password. Asks the user for the old password
    and the new password twice.
    If the first new password matches the second, it sets a new password
    to the user and sends the user to the main page.
    """

    # template_name = "profiles/password_form.html"
    template_name = "profiles/password_form.jinja2"
    success_url = reverse_lazy("profiles:home-page")
