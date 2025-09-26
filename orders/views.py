from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import BaseSerializer
from django.db.models import Q, QuerySet, Count
from django.contrib.auth.models import AnonymousUser
from orders.models import Order
from orders.serializers import (
    OrderSerializer,
    OrderSummaryListSerializer,
    OrderFilterSerializer,
)
from typing import Any


class OrderListCreateView(ListCreateAPIView[Order]):
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Order]:
        user = self.request.user
        assert not isinstance(user, AnonymousUser)

        serializer: OrderFilterSerializer = OrderFilterSerializer(
            data=self.request.query_params
        )
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        filters = Q()

        if "status" in params:
            filters &= Q(status__iexact=params["status"])
        if "min_total" in params:
            filters &= Q(total_price__gte=params["min_total"])
        if "max_total" in params:
            filters &= Q(total_price__lte=params["max_total"])
        if "start_date" in params:
            filters &= Q(created_at__date__gte=params["start_date"])
        if "end_date" in params:
            filters &= Q(created_at__date__lte=params["end_date"])

        qs: QuerySet[Order] = (
            Order.objects.filter(filters, user=user)
            .prefetch_related("order_items")
            .annotate(items_count=Count("order_items"))
        )

        # Ordering
        ordering = params.get("ordering", "-created_at")
        qs = qs.order_by(ordering)

        return qs

    def get_serializer_class(
        self,
    ) -> type[OrderSerializer] | type[OrderSummaryListSerializer]:
        if self.request.method == "GET":
            return OrderSummaryListSerializer
        return OrderSerializer

    def perform_create(self, serializer: Any) -> None:
        serializer.save(user=self.request.user)


class OrderDetailView(RetrieveUpdateDestroyAPIView[Order]):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self) -> QuerySet[Order]:
        user = self.request.user
        assert not isinstance(user, AnonymousUser)
        return Order.objects.filter(user=user).prefetch_related("order_items__product")

    def perform_update(self, serializer: BaseSerializer[Order]) -> None:
        order = self.get_object()
        if order.status != "pending":
            raise PermissionDenied("Only pending orders can be updated.")
        serializer.save()

    def perform_destroy(self, instance: Order) -> None:
        if instance.status != "pending":
            raise PermissionDenied("Only pending orders can be cancelled (deleted).")
        instance.delete()
