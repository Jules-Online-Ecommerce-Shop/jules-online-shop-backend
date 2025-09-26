from django.db.models.signals import post_save, post_delete
from django.db.models import Sum, F
from django.dispatch import receiver
from .models import OrderItem, Order
from typing import Any


def recalc_order_total(order: Order) -> None:
    """
    Recalculate the total price for an order
    based on all its items.
    """
    total = (
        order.order_items.aggregate(total=Sum(F("price_snapshot") * F("quantity")))[
            "total"
        ]
        or 0
    )
    order.total_price = total
    order.save(update_fields=["total_price"])


@receiver(post_save, sender=OrderItem)
def update_order_total_on_save(
    sender: type[OrderItem], instance: OrderItem, **kwargs: Any
) -> None:
    recalc_order_total(instance.order)


@receiver(post_delete, sender=OrderItem)
def update_order_total_on_delete(
    sender: type[OrderItem], instance: OrderItem, **kwargs: Any
) -> None:
    recalc_order_total(instance.order)
