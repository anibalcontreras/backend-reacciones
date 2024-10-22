# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem

class OrderRateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

class OrderItemSerializer(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField(source='service.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'service_name', 'quantity', 'service']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)  # Serializar los ítems del pedido
    applicant_username = serializers.ReadOnlyField(source='applicant.username')
    supplier_username = serializers.ReadOnlyField(source='supplier.username')


    class Meta:
        model = Order
        fields = ['id', 'applicant_username', 'supplier_username', 'status', 'time_estimated', 'created_at', 'updated_at', 'completed_at', 'items', 'total_price', 'is_rated']
