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
