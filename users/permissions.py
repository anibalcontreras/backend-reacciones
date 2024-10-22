# users/permissions.py

from rest_framework import permissions

class IsSupplier(permissions.BasePermission):
    """
    Permiso para permitir solo a los proveedores (suppliers).
    """

    def has_permission(self, request, view):
        # Verificar si el 'user_type' es 'supplier'
        print(f"Autenticando como supplier, user_type en el usuario: {request.user.user_type}")
        
        # Si el tipo de usuario no es supplier, denegar acceso
        return request.user.is_authenticated and request.user.user_type == 'supplier'


class IsApplicant(permissions.BasePermission):
    """
    Permiso para permitir solo a los solicitantes (applicants).
    """

    def has_permission(self, request, view):
        # Verificar si el 'user_type' es 'applicant' en el objeto user
        print(f"Autenticando como applicant, user_type en el usuario: {request.user.user_type}")
        return request.user.is_authenticated and request.user.user_type == 'applicant'

