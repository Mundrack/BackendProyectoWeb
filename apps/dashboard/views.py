from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.authentication.permissions import IsOwner
from .services import StatsService
from .serializers import (
    OverviewStatsSerializer, AuditTrendSerializer, RecentAuditSerializer,
    CompanyStatsSerializer, ScoreDistributionSerializer, TemplateStatsSerializer,
    TopBranchSerializer, PeriodStatsSerializer, DashboardSummarySerializer,
    CategoryPerformanceSerializer
)


class DashboardOverviewView(APIView):
    """
    GET /api/dashboard/overview/

    Resumen general del sistema con estadísticas clave.

    Query params opcionales:
    - company_id: Filtrar por empresa específica

    Retorna:
    {
        "total_audits": 50,
        "audits_in_progress": 10,
        "completed_audits": 35,
        "average_score": 85.5,
        "total_companies": 3,
        "total_branches": 8,
        "completion_rate": 70.0
    }
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')

        stats = StatsService.get_overview_stats(
            user=request.user,
            company_id=company_id
        )

        serializer = OverviewStatsSerializer(stats)
        return Response(serializer.data)


class AuditTrendsView(APIView):
    """
    GET /api/dashboard/trends/

    Tendencias de auditorías por mes o semana (últimos 6 meses o 12 semanas).
    Optimizado para gráficos Recharts LineChart.

    Query params opcionales:
    - company_id: Filtrar por empresa
    - period: 'month' (default) o 'week'

    Retorna:
    [
        {"period": "Jan 2024", "total": 10, "completed": 8, "avg_score": 85.5},
        {"period": "Feb 2024", "total": 15, "completed": 12, "avg_score": 88.2},
        ...
    ]
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')
        period = request.query_params.get('period', 'month')

        trends = StatsService.get_audit_trends(
            user=request.user,
            company_id=company_id,
            period=period
        )

        serializer = AuditTrendSerializer(trends, many=True)
        return Response(serializer.data)


class RecentAuditsView(APIView):
    """
    GET /api/dashboard/recent-audits/

    Auditorías recientes (últimas 10 por defecto).

    Query params opcionales:
    - company_id: Filtrar por empresa
    - limit: Cantidad de resultados (default: 10)

    Retorna:
    [
        {
            "id": 1,
            "title": "Auditoría ISO 9001 - Enero",
            "company_name": "Empresa X",
            "branch_name": "Sucursal Centro",
            "status": "completed",
            "score_percentage": 85.5,
            "created_at": "2024-01-15",
            "completed_at": "2024-01-20"
        },
        ...
    ]
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')
        limit = int(request.query_params.get('limit', 10))

        audits = StatsService.get_recent_audits(
            user=request.user,
            company_id=company_id,
            limit=limit
        )

        serializer = RecentAuditSerializer(audits, many=True)
        return Response(serializer.data)


class CompanyStatsView(APIView):
    """
    GET /api/dashboard/company-stats/

    Estadísticas agrupadas por empresa.
    Optimizado para Recharts BarChart.

    Query params opcionales:
    - company_id: Filtrar por empresa específica

    Retorna:
    [
        {
            "company_id": 1,
            "company_name": "Empresa X",
            "total_audits": 25,
            "completed": 20,
            "avg_score": 88.5,
            "branches_count": 5
        },
        ...
    ]
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')

        stats = StatsService.get_company_stats(
            user=request.user,
            company_id=company_id
        )

        serializer = CompanyStatsSerializer(stats, many=True)
        return Response(serializer.data)


class ScoreDistributionView(APIView):
    """
    GET /api/dashboard/score-distribution/

    Distribución de puntajes en rangos (0-20, 21-40, etc.).
    Optimizado para Recharts BarChart o PieChart.

    Query params opcionales:
    - company_id: Filtrar por empresa

    Retorna:
    [
        {"range": "0-20", "count": 2},
        {"range": "21-40", "count": 5},
        {"range": "41-60", "count": 8},
        {"range": "61-80", "count": 15},
        {"range": "81-100", "count": 20}
    ]
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')

        distribution = StatsService.get_score_distribution(
            user=request.user,
            company_id=company_id
        )

        serializer = ScoreDistributionSerializer(distribution, many=True)
        return Response(serializer.data)


class TemplateStatsView(APIView):
    """
    GET /api/dashboard/template-stats/

    Estadísticas de uso de plantillas (cuántas auditorías por plantilla).
    Optimizado para Recharts BarChart o PieChart.

    Query params opcionales:
    - company_id: Filtrar por empresa

    Retorna:
    [
        {
            "template_id": 1,
            "template_name": "ISO 9001",
            "total_audits": 25,
            "completed": 20,
            "avg_score": 88.5
        },
        ...
    ]
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')

        stats = StatsService.get_audits_by_template(
            user=request.user,
            company_id=company_id
        )

        serializer = TemplateStatsSerializer(stats, many=True)
        return Response(serializer.data)


class TopBranchesView(APIView):
    """
    GET /api/dashboard/top-branches/

    Mejores sucursales por puntaje promedio (solo auditorías completadas).

    Query params opcionales:
    - company_id: Filtrar por empresa
    - limit: Cantidad de resultados (default: 10)

    Retorna:
    [
        {
            "branch_id": 1,
            "branch_name": "Sucursal Centro",
            "company_name": "Empresa X",
            "total_audits": 10,
            "avg_score": 92.5
        },
        ...
    ]
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')
        limit = int(request.query_params.get('limit', 10))

        branches = StatsService.get_top_performing_branches(
            user=request.user,
            company_id=company_id,
            limit=limit
        )

        serializer = TopBranchSerializer(branches, many=True)
        return Response(serializer.data)


class PeriodStatsView(APIView):
    """
    GET /api/dashboard/period-stats/

    Estadísticas del período actual (mes, semana o día).

    Query params opcionales:
    - company_id: Filtrar por empresa
    - period: 'month' (default), 'week', o 'day'

    Retorna:
    {
        "period": "December 2024",
        "total": 15,
        "completed": 12,
        "in_progress": 2,
        "draft": 1,
        "avg_score": 85.5,
        "audits": [...]
    }
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')
        period = request.query_params.get('period', 'month')

        stats = StatsService.get_audits_this_period(
            user=request.user,
            company_id=company_id,
            period=period
        )

        serializer = PeriodStatsSerializer(stats)
        return Response(serializer.data)


class CategoryPerformanceView(APIView):
    """
    GET /api/dashboard/category-performance/

    Rendimiento por categoría de preguntas (análisis avanzado).
    Optimizado para Recharts RadarChart.

    Query params opcionales:
    - company_id: Filtrar por empresa

    Retorna:
    [
        {
            "category": "Seguridad",
            "total_responses": 150,
            "avg_score": 8.5,
            "max_possible_avg": 10,
            "percentage": 85.0
        },
        ...
    ]
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')

        performance = StatsService.get_category_performance(
            user=request.user,
            company_id=company_id
        )

        serializer = CategoryPerformanceSerializer(performance, many=True)
        return Response(serializer.data)


class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary/

    Endpoint completo que combina TODAS las estadísticas del dashboard.
    Útil para cargar el dashboard completo en una sola petición.

    Query params opcionales:
    - company_id: Filtrar por empresa

    Retorna:
    {
        "overview": {...},
        "recent_audits": [...],
        "company_stats": [...],
        "score_distribution": [...],
        "template_stats": [...],
        "top_branches": [...],
        "category_performance": [...]
    }
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        company_id = request.query_params.get('company_id')
        user = request.user

        # Recopilar todas las estadísticas
        summary = {
            'overview': StatsService.get_overview_stats(user, company_id),
            'recent_audits': StatsService.get_recent_audits(user, company_id, limit=5),
            'company_stats': StatsService.get_company_stats(user, company_id),
            'score_distribution': StatsService.get_score_distribution(user, company_id),
            'template_stats': StatsService.get_audits_by_template(user, company_id),
            'top_branches': StatsService.get_top_performing_branches(user, company_id, limit=5),
            'category_performance': StatsService.get_category_performance(user, company_id)
        }

        serializer = DashboardSummarySerializer(summary)
        return Response(serializer.data)
