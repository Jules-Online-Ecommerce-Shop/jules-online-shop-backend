from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from drf_spectacular.utils import extend_schema

from .serializers import (
    EmailTokenObtainPairSerializer, MeSerializer, RegisterSerializer
)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

    @extend_schema(
        request=EmailTokenObtainPairSerializer,
        responses={200: EmailTokenObtainPairSerializer},
        description=(
            "Obtain access and refresh JWT tokens using email and password"
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=MeSerializer,
        description="Get current authenticated user info"
    )
    def get(self, request: Request) -> Response:
        user = request.user
        serializer = MeSerializer(user)

        return Response(serializer.data)


class CustomTokenRefreshView(TokenRefreshView):

    @extend_schema(
        request=TokenRefreshSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"}
                }
            }
        },
        description="Rotate refresh token to get a new access token"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RegisterView(APIView):

    @extend_schema(
        request=RegisterSerializer,
        responses={201: RegisterSerializer},
        description="Register a new user"
    )
    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
