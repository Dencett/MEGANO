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

    template_name = "profile_app/about-user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_avatar"] = ProfileAvatarUpdateForm()
        return context

    def post(self, request):
        # Need a module - pillow
        update_avatar = ProfileAvatarUpdateForm(request.POST, request.FILES)

        if update_avatar.is_valid():
            picture = update_avatar.cleaned_data.get("user_avatar")
            profile = Profile.objects.get(user=request.user)
            profile.user_avatar = picture
            profile.save()
            return HttpResponseRedirect(reverse("profile:about-user"))
        return HttpResponseRedirect(reverse("profile:about-user"))


class HomePage(TemplateView):
    """View class заглушка - главная страница сайта."""

    template_name = "profile_app/index.html"


class RegisterView(CreateView):
    """
    View class для регистрации пользователей. Если данные из формы валидны,
    авторизовывает пользователя и перенаправляет на главную страницу сайта.
    """

    form_class = UserRegisterForm
    template_name = "profile_app/register.html"
    success_url = reverse_lazy("profile:home-page")

    def form_valid(self, form):
        response = super().form_valid(form)

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
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
            username=username,
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


class MyLogoutView(LogoutView):
    """View class заглушка - user logout."""

    next_page = reverse_lazy("profile:home-page")


class UserResetPasswordViewTwo(PasswordChangeView):
    template_name = "profile_app/password_form.html"
    success_url = reverse_lazy("profile:home-page")
