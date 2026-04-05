from django.urls import path
from .views import (
    EmailTokenObtainPairView,
    MeView,
    CustomTokenRefreshView,
    RegisterView,
)


urlpatterns = [
    path(
        "login/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("register/", RegisterView.as_view(), name="register"),
]
