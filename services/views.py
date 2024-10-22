# services/views.py

from rest_framework import generics
from .models import Service
from .serializers import ServiceSerializer

class ServiceListView(generics.ListAPIView):
    """
    Vista para listar todos los servicios disponibles (charchazo, abrazo, etc.)
    """
    queryset = Service.objects.all()  # Obtenemos todos los servicios
    serializer_class = ServiceSerializer  # Utilizamos el serializer para convertir el queryset a JSON
