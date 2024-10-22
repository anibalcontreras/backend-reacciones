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

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Aseguramos que todos los endpoints requieran autenticación


    
    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo pedido.
        Solo los solicitantes pueden crear pedidos.
        """
        services_data = request.data.get('services', [])
        if not services_data:
            return Response({"error": "Se requiere al menos un servicio."}, status=status.HTTP_400_BAD_REQUEST)

        # Validación para asegurarse de que al menos un servicio tenga cantidad > 0
        if all(service_data.get('quantity', 0) == 0 for service_data in services_data):
            return Response({"error": "Debe haber al menos un servicio con cantidad mayor que 0."}, status=status.HTTP_400_BAD_REQUEST)

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

        # Asignar el proveedor con menos demanda (menos órdenes completadas)
        available_suppliers = User.objects.filter(user_type='supplier').order_by('order_count')
        if available_suppliers.exists():
            supplier = available_suppliers.first()  # Asigna el proveedor con menos órdenes completadas
            order.supplier = supplier

        # Guardar el precio total en la orden
        order.total_price = total_price
        order.save()

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

        # Cancelar la orden
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
    

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsApplicant])
    def rate_supplier(self, request, pk=None):
        """
        Calificar al proveedor de una orden completada.
        """
        order = self.get_object()

        # Verificar si la orden está completada
        if order.status != 'completed':
            return Response({"error": "Solo se pueden calificar órdenes completadas."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si la orden ya ha sido calificada
        if order.is_rated:
            return Response({"error": "Esta orden ya ha sido calificada."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la calificación del request
        rating = request.data.get('rating')
        if not rating or int(rating) not in range(1, 6):
            return Response({"error": "La calificación debe estar entre 1 y 5."}, status=status.HTTP_400_BAD_REQUEST)

        # Establecer la calificación
        order.set_rating(int(rating))

        return Response({"message": "Calificación registrada correctamente."}, status=status.HTTP_200_OK)


    def get_permissions(self):
        """
        Determinar los permisos para diferentes tipos de usuarios en cada acción.
        """
        if self.action == 'current_orders' or self.action == 'create' or self.action == 'rate_supplier':
            return [IsAuthenticated(), IsApplicant()]
        elif self.action == 'complete_order' or self.action == 'in_progress_orders' or self.action == 'canceled_or_completed_orders':
            return [IsAuthenticated(), IsSupplier()]
        elif self.action == 'cancel_order':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

