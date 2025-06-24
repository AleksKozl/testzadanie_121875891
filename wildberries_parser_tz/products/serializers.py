from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id", "name", "price", "discount_price",
            "rating", "reviews_count", "created_at"
        ]
