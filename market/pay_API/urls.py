from django.urls import path

from .views import (
    #  hello_world_view,
    megano_fake_pay,
)

# GroupsListView
# from .views import

app_name = "pay_API"

urlpatterns = [
    # path('hello/', hello_world_view, name='hello'),
    path("meganopay/", megano_fake_pay, name="pay")
]
