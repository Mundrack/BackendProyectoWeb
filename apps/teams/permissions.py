from rest_framework import permissions


class IsCompanyOwnerForTeam(permissions.BasePermission):
    """
    Permiso: Solo el owner de la empresa puede gestionar equipos
    """

    message = 'Solo el propietario de la empresa puede gestionar equipos.'

    def has_object_permission(self, request, view, obj):
        # obj puede ser Team o TeamMember
        if hasattr(obj, 'department'):
            # Es un Team
            return obj.department.branch.company.owner == request.user
        elif hasattr(obj, 'team'):
            # Es un TeamMember
            return obj.team.department.branch.company.owner == request.user

        return False
