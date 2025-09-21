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

    class Meta:  # type: ignore
        verbose_name_plural = "Categories"
        unique_together = ["slug", "parent"]
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
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
