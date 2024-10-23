# services/models.py
from django.db import models

class Service(models.Model):
    SERVICE_TYPE_CHOICES = (
        ('charchazo', 'Charchazo'),
        ('abrazo', 'Abrazo'),
    )
    name = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    price = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
