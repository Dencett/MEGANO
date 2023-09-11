from django.urls import path

from .views import ExampleView

urlpatterns = [
    path("", ExampleView.as_view(), name="example"),
    # path("product/<int:pk>/", ProductDetailView.as_view(), name='Product'),
    # path("temp/", MyTemplateView.as_view(), name='temp'),
    # path('test/', myget, name='test')
]
