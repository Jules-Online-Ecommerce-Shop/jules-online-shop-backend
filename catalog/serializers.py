from rest_framework import serializers
from catalog.models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "name",
            "slug",
            "description",
            "parent",
            "full_slug",
            "children"
        ]
        read_only_fields = ["children"]

    def get_children(self, obj: Category):
        return CategorySerializer(
            obj.children.all(),
            many=True,
            context=self.context
        ).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_featured"]


class ProductSerializer(serializers.ModelSerializer):
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


class ProductFilterSerializer(serializers.Serializer):
    category = serializers.CharField(required=False)
    brand = serializers.CharField(required=False)
    min_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2
    )
    max_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2
    )
    in_stock = serializers.BooleanField(required=False)
