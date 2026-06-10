from django.urls import path

from .views import (
    CartView,
    CartItemCreateView,
    CartItemDetailView,
    CartCheckoutView,
    CartCountView,
    OrderListView,
    OrderDetailView,
    OrderPayView,
)

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/items/", CartItemCreateView.as_view(), name="cart-item-create"),
    path(
        "cart/items/<int:item_id>/",
        CartItemDetailView.as_view(),
        name="cart-item-detail",
    ),
    path("cart/checkout/", CartCheckoutView.as_view(), name="cart-checkout"),
    path("cart/count/", CartCountView.as_view(), name="cart-count"),
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/pay/", OrderPayView.as_view(), name="order-pay"),
]
