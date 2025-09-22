from django.contrib import admin
from django.utils.html import format_html
from catalog.models import Category, Product, ProductImage
from unfold.admin import ModelAdmin, TabularInline


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "full_slug", "parent")
    search_fields = ("name", "slug")
    list_filter = ("parent",)
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"
    image_tag.short_description = "Image"


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("name", "slug", "price", "stock_quantity", "category", "brand", "is_active")
    search_fields = ("name", "slug", "brand")
    list_filter = ("category", "brand", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ("id", "product", "image_tag")
    list_filter = ("product",)
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"
    image_tag.short_description = "Image"
