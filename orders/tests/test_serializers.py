from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from catalog.models import Product, ProductImage
from orders.models import Order, OrderItem
from orders.serializers import (
    ProductSummarySerializer,
    OrderItemSerializer,
    OrderSerializer,
    OrderSummaryListSerializer,
    OrderFilterSerializer
)

User = get_user_model()


class SerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="password")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("99.99"),
            stock_quantity=10,
            brand="BrandX",
            imported_from="GH",
            is_active=True
        )
        ProductImage.objects.create(product=self.product, image="path/to/image.jpg", is_featured=True)
        self.order = Order.objects.create(
            user=self.user,
            status="pending",
            total_price=Decimal("199.98"),
            shipping_name="John Doe",
            shipping_address_line1="123 Main St",
            shipping_address_line2="Apt 4",
            shipping_digital_address="GD-1234",
            shipping_region="Greater Accra",
            shipping_country="Ghana"
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_snapshot=self.product.price
        )

    def test_product_summary_serializer(self) -> None:
        serializer = ProductSummarySerializer(self.product)
        data = serializer.data
        self.assertEqual(data["id"], str(self.product.id))
        self.assertIn("image", data)
        self.assertIsNotNone(data["image"])

    def test_order_item_serializer(self) -> None:
        serializer = OrderItemSerializer(self.order_item)
        data = serializer.data
        self.assertEqual(data["quantity"], self.order_item.quantity)
        self.assertIn("product_summary", data)

    def test_order_serializer(self) -> None:
        serializer = OrderSerializer(self.order)
        data = serializer.data
        self.assertEqual(data["id"], str(self.order.id))
        self.assertEqual(len(data["order_items"]), 1)

    def test_order_summary_list_serializer(self) -> None:
        self.order.items_count = self.order.order_items.count()
        serializer = OrderSummaryListSerializer(self.order)
        data = serializer.data
        self.assertEqual(data["items_count"], 1)

    def test_order_filter_serializer_valid(self) -> None:
        data = {"status": "pending", "ordering": "-total_price"}
        serializer = OrderFilterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_order_filter_serializer_invalid(self) -> None:
        data = {"status": "invalid"}
        serializer = OrderFilterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)
