from django.contrib import admin
from unfold.admin import UnfoldedModelAdmin, UnfoldedTabularInline
from .models import Cart, CartItem


class CartItemInline(UnfoldedTabularInline):
    """
    Inline for CartItem inside Cart admin.
    Shows product, quantity, and price snapshot.
    Supports sorting by subtotal.
    """
    model: type[CartItem] = CartItem
    extra: int = 0
    readonly_fields = ("product_name", "price_snapshot", "sub_total_display")
    fields = ("product_name", "quantity", "price_snapshot", "sub_total_display")
    can_delete: bool = True
    show_change_link: bool = True

    @admin.display(description="Product")
    def product_name(self, obj: CartItem) -> str:
        return obj.product.name

    @admin.display(
        description="Subtotal",
        ordering="price_snapshot"
    )
    def sub_total_display(self, obj: CartItem) -> str:
        """Formatted display of subtotal for inline."""
        return f"${obj.sub_total:.2f}"


@admin.register(Cart)
class CartAdmin(UnfoldedModelAdmin):
    """
    Admin interface for Cart.
    Uses django-unfold to show CartItems as folded inline.
    total_price and total_items are sortable.
    """
    list_display = (
        "user",
        "total_items",
        "total_price_display",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "user__email")
    inlines = [CartItemInline]
    readonly_fields = ("total_items", "total_price_display")
    list_filter = ("created_at", "updated_at")

    @admin.display(description="Items Count", ordering="items__count")
    def total_items(self, obj: Cart) -> int:
        return obj.items.count()

    @admin.display(description="Total Price", ordering="items__price_snapshot")
    def total_price_display(self, obj: Cart) -> str:
        """Formatted display for total price (sortable by total)."""
        return f"${obj.total:.2f}"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin[CartItem]):
    """
    Optional standalone CartItem admin for direct access.
    Supports sorting by subtotal.
    """
    list_display = (
        "product",
        "cart",
        "quantity",
        "price_snapshot",
        "sub_total_display",
    )
    search_fields = ("product__name", "cart__user__username")
    readonly_fields = ("sub_total_display",)
    list_filter = ("cart",)

    @admin.display(description="Subtotal", ordering="price_snapshot")
    def sub_total_display(self, obj: CartItem) -> str:
        return f"${obj.sub_total:.2f}"
