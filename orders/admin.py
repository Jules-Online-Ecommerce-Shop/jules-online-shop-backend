from django.contrib import admin
from orders.models import Order, OrderItem
from unfold.admin import ModelAdmin, TabularInline


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price_snapshot", "created_at", "updated_at")


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
    search_fields = ("user__email", "shipping_name", "shipping_address_line1", "shipping_region")
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price_snapshot", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("order__id", "product__name")
    readonly_fields = ("created_at", "updated_at")
