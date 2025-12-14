from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, QuerySet, Count
from django.contrib.auth.models import AnonymousUser
from orders.models import Order
from orders.serializers import (
    OrderSerializer,
    OrderSummaryListSerializer,
    OrderFilterSerializer,
)
from typing import Any


@extend_schema(
    tags=["Orders"],
    summary="List all user orders",
    description=(
        "Retrieves a list of the authenticated user's orders.\n\n"
        "Supports filtering by:\n"
        "- **status** (pending, paid, shipped, completed, cancelled)\n"
        "- **min_total** and **max_total** (price range)\n"
        "- **start_date** and **end_date** (creation date range)\n"
        "- **ordering** (e.g., `-created_at`, `total_price`)\n\n"
        "All filters are optional."
    ),
    parameters=[
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            description=(
                "Filter by order status (e.g., pending, completed, cancelled)"
            ),
            required=False,
        ),
        OpenApiParameter(
            name="min_total",
            type=OpenApiTypes.NUMBER,
            description="Minimum total price of orders",
            required=False,
        ),
        OpenApiParameter(
            name="max_total",
            type=OpenApiTypes.NUMBER,
            description="Maximum total price of orders",
            required=False,
        ),
        OpenApiParameter(
            name="start_date",
            type=OpenApiTypes.DATE,
            description=(
                "Start date for filtering orders by creation date (YYYY-MM-DD)"
            ),
            required=False,
        ),
        OpenApiParameter(
            name="end_date",
            type=OpenApiTypes.DATE,
            description=(
                "End date for filtering orders by creation date (YYYY-MM-DD)"
            ),
            required=False,
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            description=(
                "Order results by a field (e.g., `-created_at`, `total_price`)"
            ),
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OrderSummaryListSerializer,
            description="List of user orders"
        ),
    },
)
class OrderListView(ListAPIView[Order]):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSummaryListSerializer

    def get_queryset(self) -> QuerySet[Order]:
        user = self.request.user
        assert not isinstance(user, AnonymousUser)

        serializer: OrderFilterSerializer = OrderFilterSerializer(
            data=self.request.query_params
        )
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        filters = Q(user=user)

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
            Order.objects.filter(filters)
            .prefetch_related("order_items__product__images")
            .annotate(items_count=Count("order_items"))
        )

        # Ordering
        ordering = params.get("ordering", "-created_at")

        return qs.order_by(ordering)

    def post(self, request: Request) -> Response:
        """Prevent direct order creation."""
        return Response(
            {"detail": "Orders can only be created via checkout."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@extend_schema(
    tags=["Orders"],
    summary="Retrieve, update, or cancel a specific order",
    description=(
        "This endpoint allows a user to:\n\n"
        "- **GET** → Retrieve full details of a specific order.\n"
        "- **PATCH / PUT** → Update the order *only if status is 'pending'.*\n"
        "- **DELETE** → Cancel the order (delete it) "
        "*only if status is 'pending'.*\n\n"
        "Once an order has been paid, shipped, or "
        "completed, it can no longer be modified."
    ),
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="The ID of the order to retrieve, update, or cancel",
            required=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OrderSerializer,
            description="Full details of the requested order",
        ),
        403: OpenApiResponse(
            description=(
                "Permission denied — order cannot "
                "be updated or deleted once processed."
            ),
        ),
        404: OpenApiResponse(
            description="Order not found or not owned by the current user.",
        ),
    },
)
class OrderDetailView(RetrieveUpdateDestroyAPIView[Order]):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self) -> QuerySet[Order]:
        user = self.request.user
        assert not isinstance(user, AnonymousUser)
        return Order.objects.filter(user=user).prefetch_related(
            "order_items__product__images"
        )

    def perform_update(self, serializer: Any) -> None:
        order = self.get_object()
        if order.status != "pending":
            raise PermissionDenied("Only pending orders can be updated.")
        serializer.save()

    def perform_destroy(self, instance: Order) -> None:
        if instance.status != "pending":
            raise PermissionDenied("Only pending orders can be cancelled.")
        instance.status = "cancelled"
        instance.save(update_fields=["status", "updated_at"])
