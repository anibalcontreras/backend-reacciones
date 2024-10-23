# orders/models.py
from django.db import models
from django.conf import settings  # Para importar el modelo de User
from services.models import Service
from django.utils import timezone
import random

# Función para generar el tiempo estimado aleatorio
def default_time_estimated():
    return random.randint(10, 120)

class Order(models.Model):
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applicant_orders')
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='supplier_orders')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recipient_orders')
    status = models.CharField(max_length=20, choices=(
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ), default='in_progress')
    time_estimated = models.IntegerField(default=default_time_estimated)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True, choices=[(i, str(i)) for i in range(1, 6)])
    total_price = models.PositiveIntegerField(default=0)
    is_rated = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.applicant.username}"
    
    def assign_supplier(self):
        """
        Asigna automáticamente el proveedor con menos órdenes completadas.
        """
        from users.models import User
        available_suppliers = User.objects.filter(user_type='supplier').order_by('order_count')
        if available_suppliers.exists():
            self.supplier = available_suppliers.first()
            self.save()

    def cancel(self):
        """Método para que el solicitante cancele un pedido."""
        self.status = 'cancelled'
        self.save()

    def complete(self):
        """Método para que el proveedor marque un pedido como completado.
        Restar presupuesto del solicitante y sumar al proveedor."""
        total_price = sum(item.service.price * item.quantity for item in self.items.all())

        if self.supplier:
            self.supplier.budget += total_price
            self.supplier.save()

        if self.recipient:
            self.order_count += 1
            self.recipient.save()

        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Cantidad de este tipo de servicio en el pedido

    def __str__(self):
        return f"{self.quantity} x {self.service.name} (Order #{self.order.id})"