from rest_framework.generics import ListAPIView, RetrieveAPIView
from catalog.serializers import (
    CategorySerializer,
    ProductFilterSerializer,
    ProductSerializer
)
from django.db.models import Q
from catalog.models import Category, Product


class CategoryListView(ListAPIView):
    """
    Returns all root categories with nested children
    """

    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related(
            "children",
            "children__children",
            "children__children__children",
    )


class CategoryDetailView(RetrieveAPIView):
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


class ProductListView(ListAPIView):
    """
    Returns all active products.
    Supports filtering via query params validated by a serializer.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(
        is_active=True
    ).prefetch_related("images", "category")

    def get_queryset(self):
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
        if params.get("in_stock") is True:
            filters &= Q(stock_quantity__gt=0)

        return qs.filter(filters)
