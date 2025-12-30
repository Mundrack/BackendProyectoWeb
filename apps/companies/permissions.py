from rest_framework import permissions


class IsCompanyOwner(permissions.BasePermission):
    """
    Permiso: Solo el owner de la empresa puede modificarla
    """

    message = 'Solo el propietario de la empresa puede realizar esta acción.'

    def has_object_permission(self, request, view, obj):
        # obj puede ser Company, Branch o Department
        if hasattr(obj, 'owner'):
            # Es una Company
            return obj.owner == request.user
        elif hasattr(obj, 'company'):
            # Es un Branch
            return obj.company.owner == request.user
        elif hasattr(obj, 'branch'):
            # Es un Department
            return obj.branch.company.owner == request.user

        return False


class IsCompanyOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso: Owner puede todo, otros solo lectura
    """

    def has_object_permission(self, request, view, obj):
        # Lectura permitida para todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return True

        # Escritura solo para el owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'company'):
            return obj.company.owner == request.user
        elif hasattr(obj, 'branch'):
            return obj.branch.company.owner == request.user

        return False
