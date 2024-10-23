# services/views.py

from rest_framework import generics
from .models import Service
from .serializers import ServiceSerializer

class ServiceListView(generics.ListAPIView):
    """
    Vista para listar todos los servicios disponibles (charchazo, abrazo, etc.)
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
