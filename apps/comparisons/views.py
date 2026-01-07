from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Comparison, Recommendation
from .serializers import (
    ComparisonSerializer, ComparisonCreateSerializer,
    CompareAuditsSerializer, RecommendationSerializer,
    RecommendationCreateSerializer
)
from .services.comparison_service import ComparisonService
from .services.recommendation_service import RecommendationService
from apps.authentication.permissions import IsOwner


class ComparisonViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Comparaciones guardadas.

    Permite CRUD de comparaciones y acciones especiales.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Filtrar comparaciones del owner"""
        return Comparison.objects.filter(
            created_by=self.request.user
        ).prefetch_related('audits')

    def get_serializer_class(self):
        if self.action == 'create':
            return ComparisonCreateSerializer
        return ComparisonSerializer

    @action(detail=True, methods=['get'])
    def analyze(self, request, pk=None):
        """
        GET /api/comparisons/{id}/analyze/
        Analiza una comparación guardada
        """
        comparison = self.get_object()
        audit_ids = list(comparison.audits.values_list('id', flat=True))

        try:
            analysis = ComparisonService.compare_audits(
                audit_ids=audit_ids,
                user=request.user
            )

            return Response(analysis)

        except (ValueError, DjangoValidationError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def trends(self, request, pk=None):
        """
        GET /api/comparisons/{id}/trends/
        Analiza tendencias de una comparación
        """
        comparison = self.get_object()
        audit_ids = list(comparison.audits.values_list('id', flat=True))

        try:
            trends = ComparisonService.get_trends(
                audit_ids=audit_ids,
                user=request.user
            )

            return Response(trends)

        except (ValueError, DjangoValidationError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CompareAuditsView(APIView):
    """
    POST /api/comparisons/compare/

    Compara auditorías sin guardar la comparación.
    Útil para comparaciones rápidas.

    Body: {
        "audit_ids": [1, 2, 3, 4, 5]
    }
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request):
        serializer = CompareAuditsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            comparison = ComparisonService.compare_audits(
                audit_ids=serializer.validated_data['audit_ids'],
                user=request.user
            )

            return Response(comparison)

        except (ValueError, DjangoValidationError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TrendsAnalysisView(APIView):
    """
    POST /api/comparisons/trends/

    Analiza tendencias entre auditorías sin guardar.

    Body: {
        "audit_ids": [1, 2, 3]
    }
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request):
        serializer = CompareAuditsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            trends = ComparisonService.get_trends(
                audit_ids=serializer.validated_data['audit_ids'],
                user=request.user
            )

            return Response(trends)

        except (ValueError, DjangoValidationError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RecommendationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Recomendaciones.

    Permite CRUD de recomendaciones manuales.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = RecommendationSerializer

    def get_queryset(self):
        """
        Filtrar recomendaciones:
        - Owners: de sus empresas
        - Employees: de sus auditorías asignadas
        """
        user = self.request.user

        if user.user_type == 'owner':
            return Recommendation.objects.filter(
                audit__company__owner=user
            ).select_related('audit', 'created_by')
        else:
            return Recommendation.objects.filter(
                audit__assigned_to=user
            ).select_related('audit', 'created_by')

    def get_serializer_class(self):
        if self.action == 'create':
            return RecommendationCreateSerializer
        return RecommendationSerializer


class GenerateRecommendationsView(APIView):
    """
    POST /api/audits/{audit_id}/generate-recommendations/

    Genera recomendaciones automáticas para una auditoría.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request, audit_id):
        from apps.audits.models import Audit

        try:
            audit = Audit.objects.get(
                id=audit_id,
                company__owner=request.user
            )

            if audit.status != 'completed':
                return Response(
                    {'error': 'Solo se pueden generar recomendaciones para auditorías completadas'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generar recomendaciones
            recommendations = RecommendationService.generate_recommendations(audit)

            # Obtener resumen
            summary = RecommendationService.get_recommendations_summary(audit)

            serializer = RecommendationSerializer(recommendations, many=True)

            return Response({
                'message': 'Recomendaciones generadas exitosamente',
                'summary': summary,
                'recommendations': serializer.data
            })

        except Audit.DoesNotExist:
            return Response(
                {'error': 'Auditoría no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class AuditRecommendationsView(APIView):
    """
    GET /api/audits/{audit_id}/recommendations/

    Obtiene todas las recomendaciones de una auditoría.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, audit_id):
        from apps.audits.models import Audit

        try:
            audit = Audit.objects.get(id=audit_id)

            # Verificar permisos
            if request.user.user_type == 'owner':
                if audit.company.owner != request.user:
                    return Response(
                        {'error': 'No tienes permiso para ver esta auditoría'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                if audit.assigned_to != request.user:
                    return Response(
                        {'error': 'No tienes permiso para ver esta auditoría'},
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Obtener recomendaciones
            recommendations = audit.recommendations.all()

            # Obtener resumen
            summary = RecommendationService.get_recommendations_summary(audit)

            serializer = RecommendationSerializer(recommendations, many=True)

            return Response({
                'audit_id': audit.id,
                'audit_title': audit.title,
                'summary': summary,
                'recommendations': serializer.data
            })

        except Audit.DoesNotExist:
            return Response(
                {'error': 'Auditoría no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
