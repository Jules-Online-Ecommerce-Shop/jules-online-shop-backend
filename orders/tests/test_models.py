from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from catalog.models import Product
from orders.models import Order, OrderItem

User = get_user_model()


class OrderModelTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="password"
        )
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("99.99"),
            stock_quantity=10,
            brand="BrandX",
            imported_from="GH",
            is_active=True,
        )
        self.order = Order.objects.create(
            user=self.user,
            status="pending",
            total_price=Decimal("0.00"),
            shipping_name="John Doe",
            shipping_address_line1="123 Main St",
            shipping_address_line2="Apt 4",
            shipping_digital_address="GD-1234",
            shipping_region="Greater Accra",
            shipping_country="Ghana",
        )
        super().setUp()

    def test_order_item_subtotal_and_price_snapshot(self) -> None:
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_snapshot=Decimal("0.00"),
        )
        self.assertEqual(item.price_snapshot, self.product.price)
        self.assertEqual(item.subtotal, self.product.price * 2)

    def test_order_total_price_update(self) -> None:
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_snapshot=self.product.price,
        )
        # trigger save to recalc total_price
        self.order.save()
        expected_total = self.product.price * 2
        self.assertEqual(self.order.total_price, expected_total)
