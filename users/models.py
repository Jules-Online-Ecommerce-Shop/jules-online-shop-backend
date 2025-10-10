from typing import Any
from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel
from users.managers import CustomUserManager


class User(AbstractUser, BaseModel):
    """
    Custom User model where email is the unique identifier for authentication.
    Username is still kept for display, but login is email-based.
    """

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"         # Login with email
    REQUIRED_FIELDS = ["username"]   # Username still required for superusers

    objects = CustomUserManager()  # type: ignore

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"

    def get_default_shipping_address(self) -> Any:
        return self.addresses.filter(is_default_shipping=True).first()


class UserProfile(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="users/profile_images", blank=True, null=True
    )

    def __str__(self) -> str | Any:
        return self.user.get_full_name() or self.user.email


class Address(BaseModel):
    """
    Represents a user's saved address.

    A user can have multiple addresses but only one can be marked
    as default for shipping or billing at a time.
    """

    objects = models.Manager()

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses"
    )

    full_name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    digital_address = models.CharField(max_length=50, blank=True, null=True)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="GHANA")

    # Default flags
    is_default_shipping = models.BooleanField(default=False)
    is_default_billing = models.BooleanField(default=False)

    class Meta:
        constraints = [
            # Only one default shipping address per user
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default_shipping=True),
                name="unique_default_shipping_per_user",
            ),
            # Only one default billing address per user
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default_billing=True),
                name="unique_default_billing_per_user",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.region}, {self.country}"

    # Helpers
    def set_as_default_shipping(self) -> None:
        """
        Makes this address the user's default shipping address.
        """

        if not self.pk:
            raise ValueError("Save the address before setting it as default.")

        self.__class__.objects.filter(
            user=self.user, is_default_shipping=True
        ).update(is_default_shipping=False)
        self.is_default_shipping = True
        self.save(update_fields=["is_default_shipping"])

    def set_as_default_billing(self) -> None:
        """
        Makes this address the user's default billing address.
        """

        if not self.pk:
            raise ValueError("Save the address before setting it as default.")

        self.__class__.objects.filter(
            user=self.user, is_default_billing=True
        ).update(is_default_billing=False)
        self.is_default_billing = True
        self.save(update_fields=["is_default_billing"])
