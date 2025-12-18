from rest_framework import serializers
from catalog.serializers import ProductSummarySerializer
from orders.models import Order, OrderItem

from typing import Any


class OrderItemSerializer(serializers.ModelSerializer[OrderItem]):
    product_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "quantity", "product_summary", "price_snapshot"
        ]
        read_only_fields = ["id", "product_summary", "price_snapshot"]

    def get_product_summary(self, obj: OrderItem) -> Any:
        return ProductSummarySerializer(obj.product).data


class OrderSerializer(serializers.ModelSerializer[Order]):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "total_price",
            "shipping_name",
            "shipping_address_line1",
            "shipping_address_line2",
            "shipping_digital_address",
            "shipping_region",
            "shipping_country",
            "created_at",
            "updated_at",
            "order_items"
        ]
        read_only_fields = [
            "status",
            "total_price",
            "created_at",
            "updated_at",
            "user"
        ]


class OrderSummaryListSerializer(serializers.ModelSerializer[Order]):
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price",
            "created_at",
            "updated_at",
            "items_count",
        ]
        read_only_fields = fields

    def get_items_count(self, obj: Order) -> int | Any:
        return obj.items_count  # type: ignore


class OrderFilterSerializer(serializers.Serializer[Any]):
    ordering = serializers.ChoiceField(
        choices=["total_price", "-total_price", "created_at", "-created_at"],
        required=False
    )
    status = serializers.ChoiceField(
        choices=["pending", "paid", "shipped", "delivered", "cancelled"],
        required=False
    )
    min_total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    max_total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    end_date = serializers.DateField(required=False)
    start_date = serializers.DateField(required=False)
