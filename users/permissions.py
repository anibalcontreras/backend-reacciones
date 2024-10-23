from rest_framework import permissions

class IsSupplier(permissions.BasePermission):
    """
    Permiso para permitir solo a los proveedores (suppliers).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'supplier'


class IsApplicant(permissions.BasePermission):
    """
    Permiso para permitir solo a los solicitantes (applicants).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'applicant'

