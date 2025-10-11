from rest_framework.generics import ListAPIView, RetrieveAPIView
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)
from catalog.serializers import (
    CategorySerializer,
    ProductFilterSerializer,
    ProductSerializer
)
from django.db.models import Q, QuerySet
from catalog.models import Category, Product


@extend_schema(
    summary="List Root Categories",
    description=(
        "Returns all root categories (parent__isnull=True) "
        "with nested children up to three levels deep."
    ),
    responses={200: CategorySerializer(many=True)}
)
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


@extend_schema(
    summary="Retrieve Category",
    description=(
        "Retrieve a single category by its `full_slug`"
    ),
    parameters=[
        OpenApiParameter(
            "full_slug",
            description="Full slug of the category to retrieve",
            required=True,
            type=str
        )
    ],
    responses={200: CategorySerializer}
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


@extend_schema(
    summary="List Products",
    description=(
        "Returns active products. Supports filtering by category, brand, "
        "price range, stock quantity, and in-stock status. Supports ordering "
        "by name, price, or stock_quantity (ascending or descending)."
    ),
    parameters=[
        OpenApiParameter(
            "category",
            description="Filter by category slug",
            required=False,
        ),
        OpenApiParameter(
            "brand",
            description="Filter by brand name",
            required=False
        ),
        OpenApiParameter(
            "min_price",
            description="Minimum price filter",
            required=False
        ),
        OpenApiParameter(
            "max_price",
            description="Maximum price filter",
            required=False
        ),
        OpenApiParameter(
            "stock_quantity",
            description="Minimum stock quantity",
            required=False
        ),
        OpenApiParameter(
            "in_stock",
            description="Filter only products in stock",
            required=False,
            type=bool,
        ),
        OpenApiParameter(
            "ordering",
            description=(
                "Ordering field: name, price, "
                "stock_quantity (prefix with - for descending)"
            ),
            required=False,
            type=str,
            enum=[
                "name",
                "-name",
                "price",
                "-price",
                "stock_quantity",
                "-stock_quantity",
            ],
        ),
    ],
    responses={200: ProductSerializer(many=True)},
)
class ProductListView(ListAPIView[Product]):
    """
    Returns all active products.
    Supports filtering via query params validated by a serializer.
    """
    serializer_class = ProductSerializer
    queryset = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
        .prefetch_related("images")
    )

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
        qs = qs.order_by(ordering)

        return qs.filter(filters)


@extend_schema(
    summary="Retrieve Product",
    description=(
        "Retrieve a single product by its unique slug with all "
        "related fields."
    ),
    parameters=[
        OpenApiParameter(
            "slug",
            description="Slug of the product to retrieve",
            required=True,
            type=str
        )
    ],
    responses={200: ProductSerializer}
)
class ProductDetailView(RetrieveAPIView[Product]):
    """
    Retrieve a single product by its slug.
    """
    queryset = Product.objects.prefetch_related("images", "category")
    serializer_class = ProductSerializer
    lookup_field = "slug"
