import uuid
from django.db import models

class BaseModel(models.Model):
    """
    Abstract base model that provides common fields and behavior for all database models.

    Fields:
        - id (UUIDField): Primary key using UUID for global uniqueness and security.
        - created_at (DateTimeField): Timestamp automatically set when a record is created.
        - updated_at (DateTimeField): Timestamp automatically updated whenever a record is modified.
        - is_active (BooleanField): Soft-delete/status flag to indicate whether the record is active.

    Usage:
        Inherit from BaseModel in all other models to automatically include these fields
        and ensure consistency across the database.

    Example:
        class Product(BaseModel):
            name = models.CharField(max_length=255)
            price = models.DecimalField(max_digits=10, decimal_places=2)

    Note:
        This model is abstract, so Django will not create a separate table for it.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True