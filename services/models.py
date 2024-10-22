# services/models.py
from django.db import models

class Service(models.Model):
    SERVICE_TYPE_CHOICES = (
        ('charchazo', 'Charchazo'),
        ('abrazo', 'Abrazo'),
    )
    name = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)  # Descripción opcional del servicio
    price = models.PositiveIntegerField(default=0)  # Precio del servicio
    order_count = models.PositiveIntegerField(default=0)  # Cantidad de órdenes (pedidas para solicitantes, completadas para proveedores)

    def __str__(self):
        return self.name
