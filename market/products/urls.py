from django.urls import path

from .views import HomeView, ProductView

urlpatterns = [
    path("", HomeView.as_view(), name="home-page"),
    path("product/<int:pk>/", ProductView.as_view(), name="product-detail"),
    # path("temp/", MyTemplateView.as_view(), name='temp'),
    # path('test/', myget, name='test')
]