from django.db.models import Sum
from orders.models import Order
from rest_framework.request import Request

from typing import Any


def dashboard_callback(request: Request, context: Any) -> Any:
    # compute metrics
    pending = Order.objects.filter(status="pending").count()
    shipped = Order.objects.filter(status="shipped").count()
    delivered = Order.objects.filter(status="delivered").count()
    canceled = Order.objects.filter(status="canceled").count()

    total_sales = (
        Order.objects.filter(status="delivered")
        .aggregate(sum=Sum("total_price"))["sum"]
        or 0
    )

    # add to context
    context["orders_pending"] = pending
    context["orders_shipped"] = shipped
    context["orders_delivered"] = delivered
    context["orders_canceled"] = canceled
    context["total_sales"] = total_sales

    return context
