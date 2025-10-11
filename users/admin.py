from django.contrib import admin
from django.contrib.auth import get_user_model
from unfold.admin import ModelAdmin, TabularInline
from users.models import UserProfile, Address

User = get_user_model()


class UserProfileInline(TabularInline):
    """Inline for editing UserProfile inside User admin."""

    model: type[UserProfile] = UserProfile
    can_delete: bool = False
    verbose_name_plural = "Profile"
    fields = ("phone_number", "profile_image")
    readonly_fields = ()
    extra: int = 0
    show_change_link: bool = True


class AddressInline(TabularInline):
    """Inline for editing addresses inside User admin."""

    model: type[Address] = Address
    fields = (
        "full_name",
        "address_line1",
        "address_line2",
        "digital_address",
        "region",
        "country",
        "is_default_shipping",
        "is_default_billing",
    )
    readonly_fields: tuple[str, ...] = ()
    extra: int = 0
    show_change_link: bool = True


@admin.register(User)
class UserAdmin(ModelAdmin):
    """Custom admin for User with profile and addresses inline."""

    list_display = (
        "id",
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "created_at")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)
    readonly_fields = ("last_login", "created_at", "updated_at")
    list_display_links = ("id", "email")
    icon_name = "user"
    inlines = [UserProfileInline, AddressInline]

    fieldsets = (
        ("Account Info", {"fields": ("email", "username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Important Dates", {
            "fields": ("last_login", "created_at", "updated_at")
        }),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    """Standalone UserProfile admin."""

    list_display = ("user", "phone_number", "profile_image")
    search_fields = ("user__username", "user__email", "phone_number")


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    """Standalone Address admin."""

    list_display = (
        "user",
        "full_name",
        "address_line1",
        "region",
        "country",
        "is_default_shipping",
        "is_default_billing",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__username", "user__email", "full_name", "digital_address"
    )
    list_filter = (
        "is_default_shipping", "is_default_billing", "region", "country"
    )
    readonly_fields = ("created_at", "updated_at")
