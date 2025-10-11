from decimal import Decimal
from typing import Any
from django.contrib import admin
from django.db.models import (
    Count,
    Sum,
    F,
    DecimalField,
    QuerySet,
    ExpressionWrapper
)

from django.http import HttpRequest
from unfold.admin import ModelAdmin, TabularInline
from cart.models import Cart, CartItem


class CartItemInline(TabularInline):
    """
    Inline for CartItem inside Cart admin.
    Uses django-unfold to show CartItems folded.
    Displays product name, quantity, price snapshot, and subtotal.
    """
    model: type[CartItem] = CartItem
    extra: int = 0
    readonly_fields = ("product_name", "price_snapshot", "sub_total_display")
    fields = (
        "product_name", "quantity", "price_snapshot", "sub_total_display"
    )
    can_delete: bool = True
    show_change_link: bool = True

    @admin.display(description="Product")
    def product_name(self, obj: CartItem) -> str:
        return obj.product.name

    @admin.display(description="Subtotal", ordering="subtotal")
    def sub_total_display(self, obj: CartItem) -> str:
        """
        Use annotated subtotal if available; fallback to model property.
        """
        subtotal: Decimal = getattr(obj, "subtotal", obj.sub_total)
        return f"GHS{subtotal:.2f}"


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    """
    Admin interface for Cart.
    Optimized for large datasets using annotations for total items,
    total price, and inline subtotal.
    Inline CartItems are folded using django-unfold.
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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Cart]:
        """
        Annotate total items and total price for performance.
        Also prefetch items and their products for inlines.
        Annotate each CartItem with subtotal to avoid per-row calculation.
        """
        qs: QuerySet[Cart] = super().get_queryset(request)
        return (
            qs.prefetch_related("items__product")
            .annotate(
                total_items_count=Count("items"),
                total_price_sum=Sum(
                    F("items__price_snapshot") * F("items__quantity"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            )
        )

    @admin.display(ordering="total_items_count", description="Items Count")
    def total_items(self, obj: Cart) -> int:
        return getattr(obj, "total_items_count", obj.items.count())

    @admin.display(ordering="total_price_sum", description="Total Price")
    def total_price_display(self, obj: Cart) -> str:
        total: Decimal = getattr(obj, "total_price_sum", obj.total)
        return f"GHS{total:.2f}"

    def get_inline_instances(
        self, request: HttpRequest, obj: Cart | None = None
    ) -> Any:
        """
        Annotate CartItems with subtotal
        for all inlines to improve performance.
        """
        inlines = super().get_inline_instances(request, obj)
        if obj is not None:
            # Annotate each CartItem inline queryset with subtotal
            for inline in inlines:
                if isinstance(inline, CartItemInline):
                    qs = inline.get_queryset(request)
                    inline.model = CartItem
                    inline.queryset = qs.annotate(
                        subtotal=ExpressionWrapper(
                            F("price_snapshot") * F("quantity"),
                            output_field=DecimalField(max_digits=12, decimal_places=2),
                        )
                    )
        return inlines


@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    """
    Optional standalone CartItem admin.
    Optimized with readonly subtotal display.
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

    @admin.display(description="Subtotal")
    def sub_total_display(self, obj: CartItem) -> str:
        return f"GHS{obj.sub_total:.2f}"
