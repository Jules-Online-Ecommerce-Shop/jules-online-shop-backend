from rest_framework import serializers
from catalog.models import Category, Product, ProductImage
from typing import Any


class CategorySerializer(serializers.ModelSerializer[Category]):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["name", "slug", "description", "parent", "full_slug", "children"]
        read_only_fields = ["children"]

    def get_children(self, obj: Category) -> Any:
        return CategorySerializer(
            obj.children.all(), many=True, context=self.context
        ).data


class ProductImageSerializer(serializers.ModelSerializer[ProductImage]):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_featured"]


class ProductSerializer(serializers.ModelSerializer[Product]):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "stock_quantity",
            "brand",
            "imported_from",
            "is_active",
            "category_name",
            "category_slug",
            "images",
        ]


class ProductFilterSerializer(serializers.Serializer[Any]):
    ordering = serializers.ChoiceField(
        choices=[
            "name",
            "price",
            "stock_quantity",
            "-name",
            "-price",
            "-stock_quantity",
        ],
        required=False,
    )
    category = serializers.CharField(required=False)
    brand = serializers.CharField(required=False)
    min_price = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )
    max_price = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )
    in_stock = serializers.BooleanField(required=False)
