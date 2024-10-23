from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

# Create your models here.
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('applicant', 'Applicant'),
        ('supplier', 'Supplier'),
        ('recipient', 'Recipient')
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    budget = models.PositiveIntegerField(default=5000)
    order_count = models.PositiveIntegerField(default=0)  # Cantidad de órdenes completadas (para solicitantes)
    rating = models.FloatField(null=True, blank=True)  # Promedio de calificaciones (para proveedores)
    rating_count = models.PositiveIntegerField(default=0)  # Cantidad de calificaciones recibidas

    def update_rating(self, new_rating):
        """
        Actualiza el promedio de calificaciones del proveedor.
        """
        if self.rating_count == 0:
            self.rating = new_rating
        else:
            total_rating = (self.rating * self.rating_count) + new_rating
            self.rating = total_rating / (self.rating_count + 1)
        self.rating_count += 1
        self.save()

    def __str__(self):
        return self.username
    
    def get_token(self):
        """
        Personalizamos el token JWT para incluir el tipo de usuario 'user_type'
        """
        refresh = RefreshToken.for_user(self)
        refresh['user_type'] = self.user_type  # Añadir user_type al token
        return refresh
