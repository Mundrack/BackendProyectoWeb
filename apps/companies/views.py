from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import Company, Branch, Department
from .serializers import (
    CompanySerializer, CompanyListSerializer,
    BranchSerializer, BranchListSerializer,
    DepartmentSerializer, DepartmentListSerializer
)
from .permissions import IsCompanyOwner, IsCompanyOwnerOrReadOnly


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Empresas.

    Lista, crea, actualiza y elimina empresas.
    Solo los owners pueden crear empresas.
    Solo el owner de una empresa puede editarla o eliminarla.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar empresas según el tipo de usuario:
        - Owners: solo sus empresas
        - Employees: empresas donde trabajan
        """
        user = self.request.user

        if user.user_type == 'owner':
            return Company.objects.filter(owner=user)
        else:
            # Employees ven empresas donde están asignados
            # Por ahora retornamos vacío, se implementará con Teams en Fase 3
            return Company.objects.none()

    def get_serializer_class(self):
        """Usar serializer diferente para list vs detail"""
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer

    def get_permissions(self):
        """
        Permisos específicos por acción:
        - create: solo owners
        - update/delete: solo el owner de esa empresa
        """
        if self.action in ['create']:
            from apps.authentication.permissions import IsOwner
            return [IsAuthenticated(), IsOwner()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsCompanyOwner()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Asignar automáticamente el owner"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def branches(self, request, pk=None):
        """
        Endpoint personalizado: GET /api/companies/{id}/branches/
        Obtener todas las sucursales de una empresa
        """
        company = self.get_object()
        branches = company.branches.all()
        serializer = BranchListSerializer(branches, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Endpoint personalizado: GET /api/companies/{id}/stats/
        Estadísticas de la empresa
        """
        company = self.get_object()

        stats = {
            'company_name': company.name,
            'total_branches': company.branches.count(),
            'active_branches': company.branches.filter(is_active=True).count(),
            'total_departments': Department.objects.filter(
                branch__company=company
            ).count(),
            'branches_with_manager': company.branches.filter(
                manager__isnull=False
            ).count(),
        }

        return Response(stats)


class BranchViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Sucursales.

    Lista, crea, actualiza y elimina sucursales.
    Solo el owner de la empresa puede crear/editar sucursales.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar sucursales según permisos del usuario"""
        user = self.request.user

        if user.user_type == 'owner':
            # Owners ven sucursales de sus empresas
            return Branch.objects.filter(
                company__owner=user
            ).select_related(
                'company', 'manager'
            )
        else:
            # Employees ven sucursales donde trabajan
            return Branch.objects.none()

    def get_serializer_class(self):
        """Usar serializer diferente para list vs detail"""
        if self.action == 'list':
            return BranchListSerializer
        return BranchSerializer

    def get_permissions(self):
        """Permisos: solo el owner de la empresa puede modificar"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsCompanyOwnerOrReadOnly()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Validar que el owner pueda crear sucursales en su empresa"""
        company_id = request.data.get('company')

        try:
            company = Company.objects.get(id=company_id)
            if company.owner != request.user:
                return Response(
                    {
                        'error': 'No tienes permiso para crear sucursales en esta empresa',
                        'details': {
                            'company': ['Solo el propietario puede crear sucursales']
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except Company.DoesNotExist:
            return Response(
                {
                    'error': 'Empresa no encontrada',
                    'details': {
                        'company': ['La empresa especificada no existe']
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def departments(self, request, pk=None):
        """
        Endpoint personalizado: GET /api/branches/{id}/departments/
        Obtener todos los departamentos de una sucursal
        """
        branch = self.get_object()
        departments = branch.departments.all()
        serializer = DepartmentListSerializer(departments, many=True)
        return Response(serializer.data)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Departamentos.

    Lista, crea, actualiza y elimina departamentos.
    Solo el owner de la empresa puede gestionar departamentos.
    """

    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar departamentos según permisos del usuario"""
        user = self.request.user

        if user.user_type == 'owner':
            # Owners ven departamentos de sus empresas
            return Department.objects.filter(
                branch__company__owner=user
            ).select_related('branch', 'branch__company')
        else:
            # Employees ven departamentos donde trabajan
            return Department.objects.none()

    def get_permissions(self):
        """Permisos: solo el owner de la empresa puede modificar"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsCompanyOwnerOrReadOnly()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Validar permisos al crear departamento"""
        branch_id = request.data.get('branch')

        try:
            branch = Branch.objects.select_related('company').get(id=branch_id)
            if branch.company.owner != request.user:
                return Response(
                    {
                        'error': 'No tienes permiso para crear departamentos en esta sucursal',
                        'details': {
                            'branch': ['Solo el propietario de la empresa puede crear departamentos']
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except Branch.DoesNotExist:
            return Response(
                {
                    'error': 'Sucursal no encontrada',
                    'details': {
                        'branch': ['La sucursal especificada no existe']
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return super().create(request, *args, **kwargs)
