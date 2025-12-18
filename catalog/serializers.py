from rest_framework import serializers
from catalog.models import Category, Product, ProductImage
from typing import Any

from utils.helpers import generate_optimized_url


class CategorySerializer(serializers.ModelSerializer[Category]):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "name", "slug", "description", "parent", "full_slug", "children"
        ]
        read_only_fields = ["children"]

    def get_children(self, obj: Category) -> Any:
        return CategorySerializer(
            obj.children.all(), many=True, context=self.context
        ).data


class ProductImageSerializer(serializers.ModelSerializer[ProductImage]):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_featured"]

    def get_image(self, obj: ProductImage) -> dict[str, Any]:

        # Automatically generate optimized images from Cloudinary
        return {
            "url": generate_optimized_url(
                obj.image,
                width=600,
                height=600,
                crop="fill",
            ),
            "alt_text": obj.alt_text,
        }


class ProductSummarySerializer(serializers.ModelSerializer[Product]):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "image",
            "stock_quantity",
            "brand",
        ]

    def get_image(self, obj: Product) -> dict[str, Any] | None:
        image: ProductImage | None = (
            obj.images.filter(is_featured=True).first()
            or obj.images.first()
        )

        if not image:
            return None

        # Automatically generate optimized images from Cloudinary
        return {
            "url": generate_optimized_url(
                image.image,
                width=600,
                height=600,
                crop="fill",
            ),
            "alt_text": image.alt_text,
        }


class ProductSerializer(serializers.ModelSerializer[Product]):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(
        source="category.name", read_only=True
    )
    category_slug = serializers.CharField(
        source="category.slug", read_only=True
    )

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
