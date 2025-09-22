from django.urls import path
from catalog import views

urlpatterns = [
    path(
        "categories/",
        views.CategoryListView.as_view(),
        name="category-list"
    ),
    path(
        "categories/<path:full_slug>/",
        views.CategoryDetailView.as_view(),
        name="category-detail"
    ),
    path(
        "products/",
        views.ProductListView.as_view(),
        name="product-list"
    ),
    path(
        "products/<slug:slug>/",
        views.ProductDetailView.as_view(),
        name="product-detail"
    )
]
