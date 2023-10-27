from rest_framework import serializers
from .custom_validators import even_number


class MeganoOrderSerializer(serializers.Serializer):
    identify_number = serializers.IntegerField()
    cart_number = serializers.IntegerField(min_value=10000000, max_value=100000000)
    price = serializers.DecimalField(max_digits=None, decimal_places=2)


class MeganoOrderEvenSerializer(serializers.Serializer):
    identify_number = serializers.IntegerField()
    cart_number = serializers.IntegerField(
        min_value=10000000,
        max_value=100000000,
        validators=[
            even_number,
        ],
    )
    price = serializers.DecimalField(max_digits=None, decimal_places=2)
