from django.db import models
from core.models import BaseModel
from django.utils.text import slugify


class Category(BaseModel):
    """
    Organizes products into a hierarchical structure.
    Each category can optionally have a parent, 
    allowing nesting (e.g., Clothing > Men > Shirts).
    The slug is auto-generated from the name for clean, SEO-friendly URLs.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text="Optional parent category for nested categories."
    )
    full_slug = models.CharField(max_length=500, unique=True, editable=False)

    class Meta:  # type: ignore
        verbose_name_plural = "Categories"
        unique_together = ["slug", "parent"]
        ordering = ["name"]
        indexes = [
            models.Index(fields=["full_slug"])
        ]

    def save(self, *args, **kwargs):
        force_update = kwargs.pop("force_full_slug_update", False)

        # Generate slug if empty
        if not self.slug:
            self.slug = slugify(self.name)

        # Check if slug or parent changed
        old_slug = old_parent_id = None
        if self.pk:
            old_self = Category.objects.filter(pk=self.pk).only("slug", "parent").first()
            if old_self:
                old_slug = old_self.slug
                old_parent_id = old_self.parent_id

        needs_update = (
            force_update
            or self.pk is None
            or self.slug != old_slug
            or self.parent_id != old_parent_id
        )

        if needs_update:
            # Compute full_slug from current tree
            self.full_slug = self.get_full_slug()
            super().save(*args, **kwargs)

            # Recursively update children
            for child in self.children.all():
                child.save(force_full_slug_update=True)
        else:
            super().save(*args, **kwargs)

    def get_full_slug(self) -> str:
        """
        Build the full path: eg clothing/men/shirts
        """
        parts: list[str] = [self.slug]
        parent: Category | None = self.parent
        while parent is not None:
            parts.insert(0, parent.slug)
            parent = parent.parent

        return "/".join(parts)

    def __str__(self):
        return self.name


class Product(BaseModel):
    """
    Represents a product in the catalog
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )
    brand = models.CharField(max_length=255, blank=True)
    imported_from = models.CharField(max_length=255, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"])
        ]

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Ensure slug is unique
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(BaseModel):
    """
    Represents an image for a product.
    A product can have multiple images.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/images/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_featured", "id"]

    def __str__(self):
        return f"{self.product.name} - {self.alt_text or 'Image'}"
