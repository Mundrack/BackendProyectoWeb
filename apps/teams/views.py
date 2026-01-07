from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Count
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Team, TeamMember
from .serializers import (
    TeamSerializer, TeamListSerializer,
    TeamMemberSerializer, TeamMemberListSerializer,
    AddMemberSerializer, ChangeMemberRoleSerializer
)
from .services.team_service import TeamService
from .permissions import IsCompanyOwnerForTeam
from apps.authentication.permissions import IsOwner


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Equipos.

    Permite CRUD completo y acciones especiales.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar equipos según el tipo de usuario:
        - Owners: equipos de sus empresas
        - Employees: equipos donde están asignados
        """
        user = self.request.user

        queryset = Team.objects.select_related(
            'department__branch__company', 'leader'
        ).prefetch_related('members')

        if user.user_type == 'owner':
            # Owners ven equipos de sus empresas
            queryset = queryset.filter(
                department__branch__company__owner=user
            )
        else:
            # Employees ven equipos donde están asignados
            queryset = queryset.filter(
                members__user=user
            ).distinct()

        # Filtros opcionales
        company_id = self.request.query_params.get('company')
        if company_id:
            queryset = queryset.filter(
                department__branch__company_id=company_id
            )

        branch_id = self.request.query_params.get('branch')
        if branch_id:
            queryset = queryset.filter(
                department__branch_id=branch_id
            )

        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        team_type = self.request.query_params.get('team_type')
        if team_type:
            queryset = queryset.filter(team_type=team_type)

        return queryset.annotate(member_count=Count('members'))

    def get_serializer_class(self):
        """Usar serializer diferente según la acción"""
        if self.action == 'list':
            return TeamListSerializer
        return TeamSerializer

    def get_permissions(self):
        """Permisos: solo owners pueden crear/modificar equipos"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwner(), IsCompanyOwnerForTeam()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """
        POST /api/teams/{id}/add-member/
        Agrega un miembro al equipo

        Body: {
            "user_id": 5,
            "role": "member"  // o "leader"
        }
        """
        team = self.get_object()
        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            member = TeamService.add_member_to_team(
                team_id=team.id,
                user_id=serializer.validated_data['user_id'],
                role=serializer.validated_data['role']
            )

            return Response({
                'message': 'Miembro agregado exitosamente',
                'member': TeamMemberSerializer(member).data
            })

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """
        POST /api/teams/{id}/remove-member/
        Remueve un miembro del equipo

        Body: {
            "user_id": 5
        }
        """
        team = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            TeamService.remove_member_from_team(
                team_id=team.id,
                user_id=user_id
            )

            return Response({
                'message': 'Miembro removido exitosamente'
            })

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def change_member_role(self, request, pk=None):
        """
        POST /api/teams/{id}/change-member-role/
        Cambia el rol de un miembro

        Body: {
            "user_id": 5,
            "new_role": "leader"  // o "member"
        }
        """
        team = self.get_object()
        serializer = ChangeMemberRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            member = TeamService.change_member_role(
                team_id=team.id,
                user_id=serializer.validated_data['user_id'],
                new_role=serializer.validated_data['new_role']
            )

            return Response({
                'message': 'Rol actualizado exitosamente',
                'member': TeamMemberSerializer(member).data
            })

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        GET /api/teams/{id}/stats/
        Obtiene estadísticas del equipo
        """
        team = self.get_object()

        try:
            stats = TeamService.get_team_stats(team.id)
            return Response(stats)

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TeamMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Miembros de Equipo.
    """

    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar miembros según permisos"""
        user = self.request.user

        queryset = TeamMember.objects.select_related(
            'team__department__branch__company', 'user'
        )

        if user.user_type == 'owner':
            # Owners ven miembros de sus empresas
            queryset = queryset.filter(
                team__department__branch__company__owner=user
            )
        else:
            # Employees ven miembros de sus equipos
            queryset = queryset.filter(
                team__members__user=user
            ).distinct()

        # Filtros opcionales
        team_id = self.request.query_params.get('team')
        if team_id:
            queryset = queryset.filter(team_id=team_id)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return TeamMemberListSerializer
        return TeamMemberSerializer

    def get_permissions(self):
        """Permisos: solo owners pueden modificar"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwner(), IsCompanyOwnerForTeam()]
        return super().get_permissions()


class HierarchyView(APIView):
    """
    GET /api/teams/hierarchy/

    Obtiene la jerarquía organizacional completa de una empresa.

    Query params:
    - company_id: ID de la empresa (requerido)
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')

        if not company_id:
            return Response(
                {'error': 'company_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            hierarchy = TeamService.get_hierarchy(company_id)
            return Response(hierarchy)

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmployeeTeamsView(APIView):
    """
    GET /api/employees/{user_id}/teams/

    Obtiene todos los equipos de un empleado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Verificar permisos
        if request.user.user_type == 'employee' and request.user.id != user_id:
            return Response(
                {'error': 'No tienes permiso para ver los equipos de otro usuario'},
                status=status.HTTP_403_FORBIDDEN
            )

        teams = TeamService.get_employee_teams(user_id)

        return Response({
            'user_id': user_id,
            'teams_count': len(teams),
            'teams': teams
        })
