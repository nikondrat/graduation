from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from catalog.models import Photo
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)


class CartView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(
            cart,
            context={"request": request},
        )
        return Response(serializer.data)


class CartItemCreateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        photo = get_object_or_404(
            Photo, public_id=serializer.validated_data["photo_id"]
        )
        license_type = serializer.validated_data["license_type"]

        # determine price based on license type
        if license_type == "commercial":
            price = photo.price * 3
        else:
            price = photo.price

        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            photo=photo,
            license_type=license_type,
            defaults={"price": price},
        )

        if not created:
            item.price = price
            item.save()

        out = CartItemSerializer(item)
        return Response(out.data, status=status.HTTP_201_CREATED)


class CartItemDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_item(self, request, item_id):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return get_object_or_404(CartItem, id=item_id, cart=cart)

    def delete(self, request, item_id):
        item = self._get_item(request, item_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, item_id):
        item = self._get_item(request, item_id)
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_license = serializer.validated_data["license_type"]
        item.license_type = new_license
        if new_license == "commercial":
            item.price = item.photo.price * 3
        else:
            item.price = item.photo.price
        item.save()

        out = CartItemSerializer(item)
        return Response(out.data)


class CartCheckoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        items = list(cart.items.select_related("photo").all())

        if not items:
            return Response(
                {"detail": "Корзина пуста"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = sum(item.price for item in items)
        order = Order.objects.create(user=request.user, total=total)

        for item in items:
            OrderItem.objects.create(
                order=order,
                photo=item.photo,
                license_type=item.license_type,
                price=item.price,
            )

        cart.items.all().delete()

        out = OrderDetailSerializer(order)
        return Response(out.data, status=status.HTTP_201_CREATED)


class CartCountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.items.count()
        except Cart.DoesNotExist:
            count = 0
        return Response({"count": count})


class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderPayView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)

        if order.status != Order.Status.PENDING:
            return Response(
                {"detail": "Заказ уже оплачен или отменён"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = Order.Status.PAID
        order.paid_at = timezone.now()
        order.save()

        # increment download counters
        for item in order.items.all():
            Photo.objects.filter(pk=item.photo_id).update(
                downloads=models.F("downloads") + 1
            )

        out = OrderDetailSerializer(order)
        return Response(out.data)
