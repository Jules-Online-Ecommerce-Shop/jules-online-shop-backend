from decimal import Decimal
from typing import Any
from rest_framework import serializers

from cart.models import Cart, CartItem
from catalog.models import Product

from orders.models import Order
from orders.serializers import OrderSerializer, ProductSummarySerializer


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
        return obj.items_count  # type: ignore

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


class CheckoutSerializer(serializers.Serializer[Any]):
    use_default = serializers.BooleanField(default=False)
    shipping_data = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        help_text="Custom shipping details if not using default address",
    )

    def validate(self, attrs: Any) -> Any:
        """
        Only validate request structure, not business logic.
        """
        use_default = attrs.get("use_default", False)
        shipping_data = attrs.get("shipping_data")

        if not use_default and not shipping_data:
            raise serializers.ValidationError(
                "Provide shipping_data or set use_default=True."
            )

        return attrs

    def create(self, validated_data: dict[str, Any]) -> Order:
        user = self.context["request"].user
        cart = Cart.objects.filter(user=user).first()
        if not cart:
            raise serializers.ValidationError("User has no active cart.")

        try:
            order: Order = cart.checkout(
                shipping_data=validated_data.get("shipping_data"),
                use_default=validated_data.get("use_default", False),
            )
        except ValueError as e:
            # Catch model-level validation errors cleanly
            raise serializers.ValidationError(str(e))
        except Exception as e:
            # Catch unexpected errors without exposing internals
            print(str(e))
            raise serializers.ValidationError(
                "Checkout failed. Please try again later."
            )

        return order

    def to_representation(self, instance: Order) -> dict[str, Any]:
        return OrderSerializer(instance, context=self.context).data
