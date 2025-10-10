from decimal import Decimal
from typing import Any
from rest_framework import serializers

from cart.models import Cart, CartItem
from catalog.models import Product

from orders.serializers import ProductSummarySerializer


class CartItemSerializer(serializers.ModelSerializer[CartItem]):
    product = ProductSummarySerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "cart",
            "product",
            "quantity",
            "price_snapshot",
            "sub_total"
        ]
        read_only_fields = ["price_snapshot", "sub_total", "cart"]

    def get_sub_total(self, obj: CartItem) -> Decimal:
        return obj.sub_total


class CartSerializer(serializers.ModelSerializer[Cart]):
    items_count = serializers.SerializerMethodField()
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items_count",
            "total",
            "items"
        ]
        read_only_fields = ["total", "user"]

    def get_items_count(self, obj: Cart) -> int | Any:
        return obj.items_count

    def get_total(self, obj: Cart) -> Decimal:
        return obj.total


class CartItemInputSerializer(serializers.Serializer[Any]):
    """
    Validates quantity and product_id to ensure product exists

    - **Note**:
        returns 'product_id' as a **Product** instance
    """
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(
        default=1, min_value=1
    )

    def validate_product_id(self, value: Any) -> Product:
        """Ensure the product exists and is active."""
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive.")
        return product

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        return validated_data


class CartItemUpdateSerializer(serializers.Serializer[Any]):
    quantity = serializers.IntegerField(min_value=1)

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        return validated_data
