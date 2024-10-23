# orders/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsSupplier, IsApplicant
from .models import Order, OrderItem
from .serializers import OrderSerializer
from services.models import Service
from users.models import User
import random

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo pedido.
        Solo los solicitantes pueden crear pedidos.
        """
        services_data = request.data.get('services', [])
        recipient_id = request.data.get('recipient_id', None)

        if not services_data:
            return Response({"error": "Se requiere al menos un servicio."}, status=status.HTTP_400_BAD_REQUEST)

        # Validación para asegurarse de que al menos un servicio tenga cantidad > 0
        if all(service_data.get('quantity', 0) == 0 for service_data in services_data):
            return Response({"error": "Debe haber al menos un servicio con cantidad mayor que 0."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar el recipient
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response({"error": "El recipient no existe."}, status=status.HTTP_404_NOT_FOUND)

        # Crear el pedido para el solicitante autenticado
        order = Order.objects.create(applicant=request.user)

        # Crear los ítems del pedido y calcular el total del precio
        total_price = 0
        for service_data in services_data:
            try:
                service = Service.objects.get(id=service_data['service_id'])
            except Service.DoesNotExist:
                return Response({"error": f"El servicio con id {service_data['service_id']} no existe."}, status=status.HTTP_404_NOT_FOUND)

            quantity = service_data.get('quantity', 1)
            total_price += service.price * quantity  # Sumar el precio al total
            OrderItem.objects.create(order=order, service=service, quantity=quantity)

        # Verificar si el solicitante tiene pedidos en múltiplos de 5 para hacer la orden gratis
        applicant_order_count = request.user.applicant_orders.count()
        if applicant_order_count % 5 == 0:
            total_price = 0  # Orden gratis

        # Validar si el total de la orden supera el presupuesto del usuario
        if total_price > request.user.budget:
            return Response({"error": "El precio total excede tu presupuesto disponible."}, status=status.HTTP_400_BAD_REQUEST)

        # Asignar el proveedor con menos demanda (menos órdenes completadas), o aleatoriamente si todos tienen 0
        available_suppliers = User.objects.filter(user_type='supplier').order_by('order_count')

        if available_suppliers.exists():
            # Tomar el proveedor con el menor número de órdenes, pero si todos tienen el mismo número de órdenes, seleccionar aleatoriamente
            min_order_count = available_suppliers.first().order_count

            # Filtrar todos los proveedores que tienen el menor número de órdenes (incluyendo 0)
            suppliers_with_min_orders = available_suppliers.filter(order_count=min_order_count)

            # Si hay más de uno con el mismo número de órdenes, seleccionamos uno aleatoriamente
            supplier = random.choice(suppliers_with_min_orders)

        else:
            return Response({"error": "No hay proveedores disponibles."}, status=status.HTTP_400_BAD_REQUEST)

        # Asignar el proveedor seleccionado al pedido
        order.supplier = supplier
        order.total_price = total_price
        order.save()

        # Incrementar el número de órdenes del proveedor inmediatamente
        supplier.order_count += 1
        supplier.save()

        # Actualizar el presupuesto del solicitante y el número de pedidos
        if total_price > 0:  # Solo actualizar si la orden no es gratis
            request.user.budget -= total_price
        request.user.order_count += 1
        request.user.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsSupplier])
    def in_progress_orders(self, request):
        """
        Obtener las órdenes asignadas al proveedor que están en estado `in_progress`.
        Solo los proveedores pueden acceder a sus órdenes pendientes.
        """
        orders = Order.objects.filter(supplier=request.user, status='in_progress')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsSupplier])
    def canceled_or_completed_orders(self, request):
        """
        Obtener las órdenes asignadas al proveedor que están en estado `canceled` o `completed`.
        Solo los proveedores pueden acceder a sus órdenes.
        """
        orders = Order.objects.filter(supplier=request.user).exclude(status='in_progress')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsApplicant])
    def current_orders(self, request):
        """
        Obtener los pedidos vigentes del solicitante.
        Solo los solicitantes pueden acceder a sus pedidos.
        """
        orders = Order.objects.filter(applicant=request.user, status__in=['in_progress'])
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsApplicant])
    def no_current_orders(self, request):
        """
        Obtener los pedidos vigentes del solicitante.
        Solo los solicitantes pueden acceder a sus pedidos.
        """
        orders = Order.objects.filter(applicant=request.user).exclude(status='in_progress')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated])
    def cancel_order(self, request, pk=None):
        """
        Cancelar un pedido.
        Tanto los solicitantes (applicant) como los proveedores (supplier) pueden cancelar sus pedidos.
        """
        order = self.get_object()

        # Verificar si el usuario es el solicitante o el proveedor asignado
        if request.user != order.applicant and request.user != order.supplier:
            return Response({'error': 'No tienes permiso para cancelar este pedido.'}, status=status.HTTP_403_FORBIDDEN)

        # Verificar si el estado de la orden permite la cancelación
        if order.status not in ['pending', 'in_progress']:
            return Response({'error': 'Solo se pueden cancelar pedidos pendientes o en progreso.'}, status=status.HTTP_400_BAD_REQUEST)
        order.cancel()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, IsSupplier, IsApplicant])
    def complete_order(self, request, pk=None):
        """
        Marcar un pedido como completado.
        Solo los proveedores pueden marcar los pedidos como completados.
        """
        order = self.get_object()
        if order.supplier != request.user:
            return Response({'error': 'No tienes permiso para completar este pedido.'}, status=status.HTTP_403_FORBIDDEN)

        if order.status != 'in_progress':
            return Response({'error': 'Solo los pedidos en progreso se pueden completar.'}, status=status.HTTP_400_BAD_REQUEST)

        order.complete()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    def get_permissions(self):
        """
        Determinar los permisos para diferentes tipos de usuarios en cada acción.
        """
        if self.action == 'current_orders' or self.action == 'create':
            return [IsAuthenticated(), IsApplicant()]
        elif self.action == 'complete_order' or self.action == 'in_progress_orders' or self.action == 'canceled_or_completed_orders':
            return [IsAuthenticated(), IsSupplier()]
        elif self.action == 'cancel_order':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

