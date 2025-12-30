from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Permiso solo para usuarios tipo 'owner'"""

    message = 'Solo los dueños de empresa tienen acceso a este recurso.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'owner'
        )


class IsEmployee(permissions.BasePermission):
    """Permiso solo para usuarios tipo 'employee'"""

    message = 'Solo los empleados tienen acceso a este recurso.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'employee'
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Los owners pueden hacer todo, employees solo lectura"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.user_type == 'owner'
