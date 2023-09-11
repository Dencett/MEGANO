from django.urls import path

from .views import ExampleView, ProductDetailsView

urlpatterns = [
    path("", ExampleView.as_view(), name="example"),
    path("product/<int:pk>/", ProductDetailsView.as_view(), name="Product"),
    # path("temp/", MyTemplateView.as_view(), name='temp'),
    # path('test/', myget, name='test')
]
