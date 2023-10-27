import random
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from .forms import MeganoOrderEvenSerializer
from .models import ValidationError, AuthenticationError, AuthorizationError, VerificationFailed, TooManyRequests


# @api_view(["GET", ])
# def hello_world_view(request: Request) -> Response:
#     1+1
#     return Response({"message": "Hello World!"})


def random_error():
    ERRORS = (ValidationError, AuthorizationError, AuthenticationError, VerificationFailed, TooManyRequests)
    msg = "Something went wrong"
    return random.choice(ERRORS)(msg)


@api_view(
    [
        "POST",
    ]
)
def megano_fake_pay(request: Request) -> Response:
    data = request.data
    order_even = MeganoOrderEvenSerializer(data=data)
    if order_even.is_valid():
        return Response({"successfully": True, "error": ""}, status=200)
    else:
        return Response({"successfully": False, "error": f"{random_error()}"}, status=401)
