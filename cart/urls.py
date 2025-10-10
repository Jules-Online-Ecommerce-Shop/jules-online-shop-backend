from django.urls import path
from cart import views


urlpatterns = [
    path("cart/", views.CartView.as_view(), name="cart"),
    path(
        "cart/items/<uuid:item_id>",
        views.CartDetailView.as_view(),
        name="cart-detail"
    ),
]
