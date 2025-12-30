from rest_framework import permissions


class IsTemplateOwner(permissions.BasePermission):
    """
    Permiso: Solo el creador de la plantilla puede modificarla
    """

    message = 'Solo el creador de la plantilla puede realizar esta acción.'

    def has_object_permission(self, request, view, obj):
        # Lectura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True

        # obj puede ser AuditTemplate o TemplateQuestion
        if hasattr(obj, 'created_by'):
            # Es un AuditTemplate
            return obj.created_by == request.user
        elif hasattr(obj, 'template'):
            # Es un TemplateQuestion
            return obj.template.created_by == request.user

        return False
