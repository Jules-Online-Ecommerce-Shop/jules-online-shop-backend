from decimal import Decimal, ROUND_HALF_UP
from django.db import models, transaction
from django.db.models import Sum, F, DecimalField
from django.contrib.auth import get_user_model

from catalog.models import Product

from core.models import BaseModel

User = get_user_model()


class Cart(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart"
    )

    def __str__(self) -> str:
        return f"Cart of {self.user.username}"

    @property
    def total(self) -> Decimal:
        result = self.items.aggregate(
            total=Sum(
                F("price_snapshot") * F("quantity"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )

        total = result["total"] or Decimal("0.00")
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @transaction.atomic
    def add_item(self, product: Product, quantity: int = 1) -> "CartItem":
        """
        Add an item to the current cart instance or
        update quantity if item exists
        """

        # Validate quantity
        if quantity <= 0:
            raise ValueError("quantity cannot be less/equal to zero.")

        # Try to get existing cart item
        item, created = self.items.select_for_update().get_or_create(
            product=product,
            defaults={"price_snapshot": product.price, "quantity": quantity}
        )

        # Update quantity if not created
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity", "updated_at"])

        return item

    @transaction.atomic
    def remove_item(self, product: Product) -> bool:
        """
        Remove an existing product from the cart.
        Returns True if removed, False if not found.
        """

        qs = self.items.select_for_update().filter(product=product)
        if not qs.exists():
            return False

        qs.delete()

        return True


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
