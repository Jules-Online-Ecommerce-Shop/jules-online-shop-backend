from typing import Any
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate

from users.models import User


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs.get("email")
        password = attrs.get("username")

        # Authenticate using email
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        # Use parent to generate tokens
        data = super().validate(
            {"username": user.get_username(), "password": password}
        )

        # Add user info to response
        data.update(
            {
                "user_id": user.id,
                "email": email,
                "username": user.get_username(),
                "is_staff": user.is_staff,
            }
        )

        return data


class MeSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        source="user_profile.phone_number", allow_null=True, read_only=True
    )
    profile_image = serializers.ImageField(
        source="user_profile.profile_image", allow_null=True, read_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",  # user id
            "email",
            "username",
            "is_staff",
            "phone_number",
            "profile_image",
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password_confirm"]

    def validate(self, attrs: dict[str, Any]):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")

    def create(self, validated_data: dict[str, Any]):
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user
