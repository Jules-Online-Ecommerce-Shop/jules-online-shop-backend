from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count

from cart.serializers import (
    CartItemSerializer,
    CartSerializer,
    CartItemInputSerializer,
    CartItemUpdateSerializer,
)
from cart.models import Cart, CartItem
from catalog.models import Product

from typing import Any

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve the authenticated user's cart",
        description=(
            "Fetches the current authenticated "
            "user's shopping cart, including all items, "
            "item count, and total price. If the cart does not exist, "
            "it will be created automatically."
        ),
        responses={
            200: OpenApiResponse(
                response=CartSerializer,
                description="The user's cart and its items."
            ),
        },
        tags=["Cart"],
        examples=[
            OpenApiExample(
                "Cart Example",
                value={
                    "id": "c1b2d3e4-f5a6-7890-1234-56789abcdef0",
                    "user": "user@example.com",
                    "items_count": 2,
                    "total": "199.98",
                    "items": [
                        {
                            "id": "item-uuid-1",
                            "cart": "c1b2d3e4-f5a6-7890-1234-56789abcdef0",
                            "product": {
                                "id": "prod-uuid-1",
                                "name": "Product 1",
                                "price": "99.99",
                                # ...other fields...
                            },
                            "quantity": 2,
                            "price_snapshot": "99.99",
                            "sub_total": "199.98",
                        }
                    ],
                },
                response_only=True,
            )
        ],
    ),
    post=extend_schema(
        summary="Add or increase a product in the cart",
        description=(
            "Adds a product to the authenticated user's "
            "cart or increases its quantity if it already exists. "
            "Returns the updated cart. The product must be active."
        ),
        request=CartItemInputSerializer,
        responses={
            201: OpenApiResponse(
                response=CartSerializer,
                description="Product added to cart (new item)."
            ),
            200: OpenApiResponse(
                response=CartSerializer,
                description="Product quantity increased (existing item).",
            ),
            400: OpenApiResponse(
                description="Invalid input or product not found."
            ),
        },
        tags=["Cart"],
    ),
    delete=extend_schema(
        summary="Clear the authenticated user's cart",
        description="Removes all items from the authenticated user's cart.",
        responses={
            204: OpenApiResponse(description="Cart cleared successfully."),
        },
        tags=["Cart"],
    ),
)
class CartView(APIView):
    """
    Cart API

    Manage the authenticated user's shopping cart.
    Supports retrieving the cart, adding products, and clearing all items.
    All endpoints require authentication.
    """

    permission_classes = [IsAuthenticated]

    def get_cart(self, user: Any) -> Cart:
        cart, _ = Cart.objects.get_or_create(user=user)

        # Annotate items_count and prefetch items
        cart = (
            Cart.objects
            .annotate(items_count=Count("items", distinct=True))
            .prefetch_related("items__product__images")
            .get(id=cart.id)
        )
        return cart

    def get(self, request: Request) -> Response:
        """
        Retrieve the user's cart.
        """
        cart: Cart = self.get_cart(request.user)
        serializer: CartSerializer = CartSerializer(
            cart, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """
        Add or increase the quantity of a product in the cart.
        """
        serializer: CartItemInputSerializer = CartItemInputSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        product: Product = (
            serializer.validated_data["product_id"]
        )  # Already Product instance
        quantity = serializer.validated_data["quantity"]

        cart = self.get_cart(request.user)
        _, created = cart.add_item(product, quantity)

        output_serializer = CartSerializer(cart, context={"request": request})
        status_code = (
            status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
        return Response(output_serializer.data, status=status_code)

    def delete(self, request: Request) -> Response:
        """
        Clear all items from the user's cart.
        """
        cart = self.get_cart(request.user)
        cart.clear_items()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a specific cart item",
        description=(
            "Fetches a specific item from the "
            "authenticated user's cart by item ID."
        ),
        parameters=[
            OpenApiParameter(
                name="item_id",
                description="UUID of the cart item",
                required=True,
                type={"type": "string", "format": "uuid"},
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=CartItemSerializer, description="Cart item details."
            ),
            404: OpenApiResponse(description="Cart or item not found."),
        },
        tags=["Cart"],
    ),
    patch=extend_schema(
        summary="Update a cart item's quantity",
        description=(
            "Partially updates the quantity of a "
            "specific item in the authenticated user's cart. "
            "Quantity must be greater than zero."
        ),
        parameters=[
            OpenApiParameter(
                name="item_id",
                description="UUID of the cart item",
                required=True,
                type={"type": "string", "format": "uuid"},
                location=OpenApiParameter.PATH,
            ),
        ],
        request=CartItemUpdateSerializer,
        responses={
            202: OpenApiResponse(
                response=CartItemSerializer,
                description="Cart item updated successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid quantity or item does not belong to cart."
            ),
            404: OpenApiResponse(description="Cart or item not found."),
        },
        tags=["Cart"],
    ),
    delete=extend_schema(
        summary="Remove a cart item",
        description=(
            "Deletes a specific item from the authenticated user's cart."
        ),
        parameters=[
            OpenApiParameter(
                name="item_id",
                description="UUID of the cart item",
                required=True,
                type={"type": "string", "format": "uuid"},
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            204: OpenApiResponse(
                description="Cart item removed successfully."
            ),
            404: OpenApiResponse(description="Cart or item not found."),
        },
        tags=["Cart"],
    ),
)
class CartDetailView(APIView):
    """
    Cart Item API

    Retrieve, update, or remove a specific item in
    the authenticated user's cart.
    All endpoints require authentication.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, item_id: UUID, user: Any) -> CartItem:
        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItem, cart_id=cart.id, id=item_id)
        return cart_item

    def get(self, request: Request, item_id: UUID) -> Response:
        """
        Retrieve a specific item in a user's cart.
        """
        item = self.get_object(item_id=item_id, user=request.user)
        serializer = CartItemSerializer(item, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, item_id: UUID) -> Response:
        """
        Partially update (e.g., quantity) of a specific item in the cart.
        """
        item: CartItem | None = self.get_object(item_id, request.user)
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data["quantity"]
        assert item is not None
        cart = item.cart

        try:
            item = cart.update_item(item=item, quantity=quantity)
        except ValueError as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = CartItemSerializer(
            item, context={"request": request}
        )
        return Response(
            output_serializer.data, status=status.HTTP_202_ACCEPTED
        )

    def delete(self, request: Request, item_id: UUID) -> Response:
        """
        Remove an item from the user's cart.
        """
        item = self.get_object(item_id, request.user)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
