from rest_framework import permissions


class IsAuditAssignedOrOwner(permissions.BasePermission):
    """
    Permiso: Solo el auditor asignado o el creador pueden acceder
    """

    message = 'Solo el auditor asignado o el creador pueden acceder a esta auditoría.'

    def has_object_permission(self, request, view, obj):
        # obj es un Audit
        return (
            obj.assigned_to == request.user or
            obj.created_by == request.user or
            (request.user.user_type == 'owner' and
             obj.company.owner == request.user)
        )
