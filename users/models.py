from typing import ClassVar
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

    objects: ClassVar[CustomUserManager] = CustomUserManager()

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"
