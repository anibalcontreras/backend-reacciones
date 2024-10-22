# services/urls.py

from django.urls import path
from .views import ServiceListView

urlpatterns = [
    path('services/', ServiceListView.as_view(), name='service-list'),
]