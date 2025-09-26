from rest_framework.generics import ListAPIView, RetrieveAPIView
from catalog.serializers import (
    CategorySerializer,
    ProductFilterSerializer,
    ProductSerializer
)
from django.db.models import Q, QuerySet
from catalog.models import Category, Product


class CategoryListView(ListAPIView[Category]):
    """
    Returns all root categories with nested children
    """

    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related(
            "children",
            "children__children",
            "children__children__children",
    )


class CategoryDetailView(RetrieveAPIView[Category]):
    """
    Retrieve a single category by full_slug with nested children
    """
    serializer_class = CategorySerializer
    lookup_field = "full_slug"
    queryset = Category.objects.prefetch_related(
            "children",
            "children__children",
            "children__children__children",
    )


class ProductListView(ListAPIView[Product]):
    """
    Returns all active products.
    Supports filtering via query params validated by a serializer.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(
        is_active=True
    ).prefetch_related("images", "category")

    def get_queryset(self) -> QuerySet[Product]:
        qs = super().get_queryset()
        filter_serializer: ProductFilterSerializer = ProductFilterSerializer(
            data=self.request.query_params
        )
        filter_serializer.is_valid(raise_exception=True)
        params = filter_serializer.validated_data

        filters: Q = Q()
        if "category" in params:
            filters &= Q(category__slug=params["category"])
        if "brand" in params:
            filters &= Q(brand__iexact=params["brand"])
        if "min_price" in params:
            filters &= Q(price__gte=params["min_price"])
        if "max_price" in params:
            filters &= Q(price__lte=params["max_price"])
        if "stock_quantity" in params:
            filters &= Q(stock_quantity__gte=params["stock_quantity"])
        if params.get("in_stock") is True:
            filters &= Q(stock_quantity__gt=0)

        # Ordering
        ordering = params.get("ordering", "name")
        allowed_fields = ["name", "price", "stock_quantity"]
        if ordering.lstrip('-') in allowed_fields:
            qs = qs.order_by(ordering)

        return qs.filter(filters)


class ProductDetailView(RetrieveAPIView[Product]):
    """
    Retrieve a single product by its slug.
    """
    queryset = Product.objects.prefetch_related("images", "category")
    serializer_class = ProductSerializer
    lookup_field = "slug"
