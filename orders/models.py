from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()


class Order(BaseModel):
    """
    Represents an instance of an order
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )

    # Shipping address snapshot
    shipping_name = models.CharField(max_length=255)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    shipping_digital_address = models.CharField(max_length=20)
    shipping_region = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100, default="GHANA")

    def __str__(self) -> str:
        return f"Order {self.id} - {self.user.email}"


class OrderItem(BaseModel):
    """
    Represents an item in an order
    """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
