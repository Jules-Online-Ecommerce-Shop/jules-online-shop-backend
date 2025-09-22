from django.urls import path
from catalog import views

urlpatterns = [
    path(
        "categories/",
        views.CategoryListView.as_view(),
        name="category-list"
    ),
    path(
        "categories/<path:full_slug>",
        views.CategoryDetailView.as_view(),
        name="category-detail"
    ),
]
