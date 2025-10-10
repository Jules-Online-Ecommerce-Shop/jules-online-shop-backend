from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional
from django.db import models, transaction
from django.db.models import Sum, F, DecimalField
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from catalog.models import Product

from core.models import BaseModel
from orders.models import Order, OrderItem
from users.models import Address

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
    def add_item(
        self, product: Product, quantity: int = 1
    ) -> tuple["CartItem", bool]:
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

        return item, created

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

    @transaction.atomic
    def update_item(
        self,
        *,
        product: Optional[Product] = None,
        item: Optional["CartItem"] = None,
        quantity: int
    ) -> Optional["CartItem"]:
        """
        Update the quantity of a cart item, given either the item instance
        or the product. Returns the updated CartItem, or None if not found.

        Ensures atomicity and row-level locking for safe concurrent updates.
        """
        # Validate quantity
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        # If item is not provided, try fetching via product
        if item is None:
            if not product:
                raise ValueError(
                    "Either 'item' or 'product' must be provided."
                )
            try:
                item = (
                    self.items
                    .select_for_update()
                    .get(product=product)
                )
            except CartItem.DoesNotExist:
                return None
        else:
            # Safety: ensure this item belongs to this cart
            if item.cart_id != self.id:
                raise ValueError(
                    "The provided item does not belong to this cart."
                )

        # Perform update
        item.quantity = quantity
        item.save(update_fields=["quantity", "updated_at"])

        return item

    @transaction.atomic
    def clear_items(self) -> None:
        """Remove all items from the cart."""
        self.items.all().delete()

    @transaction.atomic
    def checkout(
        self,
        shipping_data: dict[str, Any] | None = None,
        use_default: bool = False,
    ) -> Order:
        """
        Converts the cart into an order.
        User can either use their default shipping
        address or provide a custom one.
        """
        if not self.items.exists():
            raise ValueError("Cannot checkout an empty cart.")

        # Determine shipping info
        if use_default:
            address: Address | None = self.user.get_default_shipping_address()
            if not address:
                raise ValueError("No default shipping address set.")
            shipping_data = {
                "shipping_name": address.full_name,
                "shipping_address_line1": address.address_line1,
                "shipping_address_line2": address.address_line2,
                "shipping_digital_address": address.digital_address,
                "shipping_region": address.region,
                "shipping_country": address.country,
            }
        elif not shipping_data:
            raise ValueError(
                "Shipping address must be provided if not using default."
            )

        # Validate required fields
        required_fields = [
            "shipping_name",
            "shipping_address_line1",
            "shipping_digital_address",
            "shipping_region",
            "shipping_country",
        ]
        for f in required_fields:
            if not shipping_data.get(f):
                raise ValueError(f"Missing required shipping field: {f}")

        # Create order with shipping snapshot
        order: Order = Order.objects.create(
            user=self.user,
            **{k: v for k, v in shipping_data.items() if k.startswith("shipping_")},
        )

        # Create order items (snapshotting prices)
        order_items: list[OrderItem] = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_snapshot=item.price_snapshot,
            )
            for item in self.items.select_related("product")
        ]
        OrderItem.objects.bulk_create(order_items)

        # Compute total from created items
        order.total_price = (
            order.order_items.aggregate(
                total=models.Sum(F("price_snapshot") * F("quantity")),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )["total"] or Decimal("0.00")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        order.save(update_fields=["total_price"])

        # Clear cart
        self.clear_items()

        return order


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
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
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
