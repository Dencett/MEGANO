from django.contrib.auth.views import LoginView
from django.urls import path
from .views import (
    HomePage,
    AboutUserView,
    UserLogoutView,
    UserRegisterView,
    UserResetPasswordView,
    UserUpdateProfileInfo,
    UserHistoryView,
)

app_name = "profiles"

urlpatterns = [
    path("", HomePage.as_view(), name="home-page"),
    path(
        "login/",
        LoginView.as_view(
            template_name="profiles/login.jinja2",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("about-user/", AboutUserView.as_view(), name="about-user"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("change_password/", UserResetPasswordView.as_view(), name="change-password"),
    path("update_info/<int:pk>/", UserUpdateProfileInfo.as_view(), name="update-info"),
    path("history/", UserHistoryView.as_view(), name="browsing_history"),
]
