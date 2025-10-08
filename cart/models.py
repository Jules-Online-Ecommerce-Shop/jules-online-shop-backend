from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.db.models import Sum, F, DecimalField
from django.contrib.auth import get_user_model

from core.models import BaseModel

User = get_user_model()


class Cart(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart"
    )

    @property
    def total(self) -> Decimal:
        result = self.items.aggregate(
            total=Sum(
                F("price_snapshot") * F("quantity"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )

        return result["total"] or Decimal("0.00")

    def __str__(self) -> str:
        return f"Cart of {self.user.username}"


class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.PROTECT, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    price_snapshot = models.DecimalField(decimal_places=2, max_digits=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_cart_product"
            )
        ]
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} (x{self.quantity})"

    @property
    def sub_total(self) -> Decimal:
        result = Decimal(self.price_snapshot) * self.quantity
        return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
