from django.contrib import admin
from orders.models import Order, OrderItem
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action
from rest_framework.request import Request
from django.db.models import QuerySet


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = (
        "price_snapshot",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("product",)
    unfold_inline_style = "tabs"


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_price",
        "shipping_region",
        "shipping_country",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "shipping_country", "shipping_region", "created_at")
    search_fields = (
        "user__email",
        "shipping_name",
        "shipping_address_line1",
        "shipping_region",
    )
    readonly_fields = ("total_price", "created_at", "updated_at")
    inlines = [OrderItemInline]

    # Optimization: reduce queries
    list_select_related = ("user",)

    # Autocomplete fields
    autocomplete_fields = ("user",)

    # Custom action
    @action(description="Mark selected orders as shipped")
    def mark_as_shipped(
        self,
        request: Request,
        queryset: QuerySet[Order]
    ) -> None:
        updated = queryset.update(status="shipped")
        self.message_user(
            request, f"{updated} order(s) successfully marked as shipped."
        )

    @action(description="Mark selected orders as delivered")
    def mark_as_delivered(
        self,
        request: Request,
        queryset: QuerySet[Order]
    ) -> None:
        updated = queryset.update(status="delivered")
        self.message_user(request, f"{updated} orders marked as delivered.")

    actions = ["mark_as_shipped", "mark_as_delivered"]

    fieldsets = [
        ("Order Info", {"fields": ["user", "status", "total_price"]}),
        ("Shipping Details", {
            "fields": [
                "shipping_name",
                "shipping_address_line1",
                "shipping_address_line2",
                "shipping_digital_address",
                "shipping_region",
                "shipping_country",
            ]
        }),
        ("Meta", {"fields": ["created_at", "updated_at"]}),
    ]


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price_snapshot",
        "created_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("order__id", "product__name")
    readonly_fields = ("created_at", "updated_at")

    list_display_links = ("id", "order")
    ordering = ("-created_at",)

    icon_name = "package"

    # Optimization
    list_select_related = ("order", "product")
    autocomplete_fields = ("order", "product")
