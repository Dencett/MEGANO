from django.contrib.auth.views import LoginView
from django.urls import path
from .views import (
    MyLogoutView,
    AboutUserView,
    RegisterView,
    HomePage,
    UserResetPasswordViewTwo,
)

app_name = "profile"

urlpatterns = [
    path("", HomePage.as_view(), name="home-page"),
    path(
        "login/",
        LoginView.as_view(
            template_name="profile_app/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-user/", AboutUserView.as_view(), name="about-user"),
    path("register/", RegisterView.as_view(), name="register"),
    path("change_password/", UserResetPasswordViewTwo.as_view(), name="change-password"),
]
