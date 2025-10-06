from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from catalog.models import Product, ProductImage
from orders.models import Order, OrderItem
from orders.views import OrderListCreateView, OrderDetailView

User = get_user_model()


class OrderViewTestCase(APITestCase):
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
        self.factory = APIRequestFactory()

    def test_order_list_view(self) -> None:
        request = self.factory.get("/orders/", {"status": "pending"})
        force_authenticate(request, user=self.user)
        view = OrderListCreateView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_order_detail_update_pending_allowed(self) -> None:
        request = self.factory.put(f"/orders/{self.order.id}/", {"status": "pending"})
        force_authenticate(request, user=self.user)
        view = OrderDetailView.as_view()
        response = view(request, pk=self.order.id)
        self.assertEqual(response.status_code, 200)

    def test_order_detail_update_non_pending_denied(self) -> None:
        self.order.status = "paid"
        self.order.save()
        request = self.factory.put(f"/orders/{self.order.id}/", {"status": "paid"})
        force_authenticate(request, user=self.user)
        view = OrderDetailView.as_view()
        with self.assertRaises(PermissionDenied):
            view(request, pk=self.order.id)

    def test_order_detail_delete_pending_allowed(self) -> None:
        request = self.factory.delete(f"/orders/{self.order.id}/")
        force_authenticate(request, user=self.user)
        view = OrderDetailView.as_view()
        response = view(request, pk=self.order.id)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_order_detail_delete_non_pending_denied(self) -> None:
        self.order.status = "paid"
        self.order.save()
        request = self.factory.delete(f"/orders/{self.order.id}/")
        force_authenticate(request, user=self.user)
        view = OrderDetailView.as_view()
        with self.assertRaises(PermissionDenied):
            view(request, pk=self.order.id)
