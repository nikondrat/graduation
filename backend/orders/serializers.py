from rest_framework import serializers

from catalog.serializers import PhotoListSerializer
from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    photo = PhotoListSerializer(read_only=True)
    licenseType = serializers.CharField(source="license_type")
    addedAt = serializers.DateTimeField(source="added_at")

    class Meta:
        model = CartItem
        fields = ("id", "photo", "licenseType", "price", "addedAt")
        read_only_fields = ("id", "price", "addedAt")


class CartItemCreateSerializer(serializers.Serializer):
    photo_id = serializers.CharField(max_length=40)
    license_type = serializers.CharField(max_length=20)

    def validate_license_type(self, value):
        allowed = ("personal", "commercial")
        if value not in allowed:
            raise serializers.ValidationError(
                f"license_type must be one of {allowed}"
            )
        return value


class CartItemUpdateSerializer(serializers.Serializer):
    license_type = serializers.CharField(max_length=20)

    def validate_license_type(self, value):
        allowed = ("personal", "commercial")
        if value not in allowed:
            raise serializers.ValidationError(
                f"license_type must be one of {allowed}"
            )
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = Cart
        fields = ("id", "items", "total", "createdAt", "updatedAt")

    def get_total(self, obj):
        return sum(item.price for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    photo = PhotoListSerializer(read_only=True)
    licenseType = serializers.CharField(source="license_type")

    class Meta:
        model = OrderItem
        fields = ("id", "photo", "licenseType", "price")


class OrderListSerializer(serializers.ModelSerializer):
    status = serializers.CharField()
    total = serializers.IntegerField()
    createdAt = serializers.DateTimeField(source="created_at")
    paidAt = serializers.DateTimeField(source="paid_at")
    itemsCount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "status", "total", "createdAt", "paidAt", "itemsCount")

    def get_itemsCount(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status = serializers.CharField()
    total = serializers.IntegerField()
    createdAt = serializers.DateTimeField(source="created_at")
    paidAt = serializers.DateTimeField(source="paid_at")

    class Meta:
        model = Order
        fields = ("id", "status", "total", "items", "createdAt", "paidAt")
