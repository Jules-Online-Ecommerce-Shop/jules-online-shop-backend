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
    CartItemUpdateSerializer
)
from cart.models import Cart, CartItem
from catalog.models import Product


from typing import Any


class CartView(APIView):
    """
    Retrieve, add to, or clear the authenticated user's cart.
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


class CartDetailView(APIView):
    """
    Retrieve, update, or delete a specific
    item in the authenticated user's cart.
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
