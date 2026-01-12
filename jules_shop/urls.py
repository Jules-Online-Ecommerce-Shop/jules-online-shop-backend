"""
URL configuration for jules_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from jules_shop.settings import DEBUG
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

base_url: str = "api/v1"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{base_url}/catalog/", include("catalog.urls")),
    path(f"{base_url}/orders/", include("orders.urls")),
    path(f"{base_url}/cart/", include("cart.urls")),

    # Spectacular docs urls
    path(f"{base_url}/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        f"{base_url}/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        f"{base_url}/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls))
    ]
    # Uncomment to enable django to server media in dev
    # urlpatterns += static(
    #     settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    # )
