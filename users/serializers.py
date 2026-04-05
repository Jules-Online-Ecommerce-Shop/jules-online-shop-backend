from typing import Any
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from users.models import User


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        data = super().validate({
            self.username_field: email,
            "password": password,
        })

        data.update({
            "user_id": self.user.id,
            "email": self.user.email,
            "is_staff": self.user.is_staff,
        })
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
        return attrs

    def create(self, validated_data: dict[str, Any]):
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user
