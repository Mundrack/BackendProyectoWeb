from django.db.models import Count, Avg, Sum, Max, Min, Q, F
from django.db.models.functions import TruncMonth, TruncWeek, TruncDate
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.audits.models import Audit, AuditResponse
from apps.companies.models import Company, Branch
from apps.templates.models import AuditTemplate


class StatsService:
    """
    Servicio para cálculos estadísticos del Dashboard.

    Métodos principales:
    - get_overview_stats(): Resumen general del sistema
    - get_audit_trends(): Tendencias de auditorías por mes/semana
    - get_recent_audits(): Auditorías recientes
    - get_company_stats(): Estadísticas por empresa
    - get_score_distribution(): Distribución de puntajes
    - get_audits_by_template(): Uso de plantillas
    - get_top_performing_branches(): Mejores sucursales
    - get_audits_this_period(): Auditorías del período actual
    """

    @staticmethod
    def _get_base_queryset(user, company_id=None):
        """
        Obtiene queryset base filtrado por usuario (owner).

        Args:
            user: Usuario autenticado (debe ser owner)
            company_id: ID de empresa para filtrar (opcional)

        Returns:
            QuerySet filtrado de auditorías
        """
        queryset = Audit.objects.filter(
            Q(company__owner=user) | Q(created_by=user)
        ).select_related('company', 'branch', 'template', 'assigned_to')

        if company_id:
            queryset = queryset.filter(company_id=company_id)

        return queryset.distinct()

    @staticmethod
    def get_overview_stats(user, company_id=None):
        """
        Resumen general del sistema.

        Returns:
            {
                'total_audits': int,
                'audits_in_progress': int,
                'completed_audits': int,
                'average_score': float,
                'total_companies': int,
                'total_branches': int,
                'completion_rate': float
            }
        """
        audits = StatsService._get_base_queryset(user, company_id)

        total_audits = audits.count()
        completed_audits = audits.filter(status='completed').count()
        audits_in_progress = audits.filter(status='in_progress').count()

        # Promedio de puntajes (solo auditorías completadas)
        completed_audits_qs = audits.filter(status='completed')
        avg_score = completed_audits_qs.aggregate(
            avg=Avg('score_percentage')
        )['avg'] or 0

        # Tasa de completitud
        completion_rate = (completed_audits / total_audits * 100) if total_audits > 0 else 0

        # Empresas y sucursales
        companies_queryset = Company.objects.filter(owner=user)
        if company_id:
            companies_queryset = companies_queryset.filter(id=company_id)

        total_companies = companies_queryset.count()
        total_branches = Branch.objects.filter(
            company__in=companies_queryset
        ).count()

        return {
            'total_audits': total_audits,
            'audits_in_progress': audits_in_progress,
            'completed_audits': completed_audits,
            'average_score': round(float(avg_score), 2),
            'total_companies': total_companies,
            'total_branches': total_branches,
            'completion_rate': round(completion_rate, 2)
        }

    @staticmethod
    def get_audit_trends(user, company_id=None, period='month'):
        """
        Tendencias de auditorías por período (mes/semana).

        Args:
            period: 'month' o 'week'

        Returns:
            [
                {'period': 'Jan 2024', 'total': 10, 'completed': 8, 'avg_score': 85.5},
                ...
            ]
        """
        audits = StatsService._get_base_queryset(user, company_id)

        # Últimos 6 meses o 12 semanas
        if period == 'month':
            truncate_func = TruncMonth
            period_format = '%b %Y'  # Jan 2024
            lookback_days = 180
        else:
            truncate_func = TruncWeek
            period_format = 'Week %U %Y'
            lookback_days = 84

        since_date = timezone.now() - timedelta(days=lookback_days)
        audits = audits.filter(created_at__gte=since_date)

        # Agrupar por período
        trends = audits.annotate(
            period=truncate_func('created_at')
        ).values('period').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            avg_score=Avg('score_percentage', filter=Q(status='completed'))
        ).order_by('period')

        # Formatear para Recharts
        result = []
        for item in trends:
            period_date = item['period']
            result.append({
                'period': period_date.strftime(period_format),
                'total': item['total'],
                'completed': item['completed'],
                'avg_score': round(float(item['avg_score'] or 0), 2)
            })

        return result

    @staticmethod
    def get_recent_audits(user, company_id=None, limit=10):
        """
        Auditorías recientes ordenadas por fecha de creación.

        Returns:
            [
                {
                    'id': 1,
                    'title': 'Auditoría...',
                    'company_name': 'Empresa X',
                    'status': 'completed',
                    'score_percentage': 85.5,
                    'created_at': '2024-01-15'
                },
                ...
            ]
        """
        audits = StatsService._get_base_queryset(user, company_id).order_by('-created_at')[:limit]

        result = []
        for audit in audits:
            result.append({
                'id': audit.id,
                'title': audit.title,
                'company_name': audit.company.name,
                'branch_name': audit.branch.name if audit.branch else None,
                'status': audit.status,
                'score_percentage': float(audit.score_percentage),
                'created_at': audit.created_at.strftime('%Y-%m-%d'),
                'completed_at': audit.completed_at.strftime('%Y-%m-%d') if audit.completed_at else None
            })

        return result

    @staticmethod
    def get_company_stats(user, company_id=None):
        """
        Estadísticas agrupadas por empresa.

        Returns:
            [
                {
                    'company_id': 1,
                    'company_name': 'Empresa X',
                    'total_audits': 15,
                    'completed': 12,
                    'avg_score': 85.5,
                    'branches_count': 3
                },
                ...
            ]
        """
        companies_queryset = Company.objects.filter(owner=user)
        if company_id:
            companies_queryset = companies_queryset.filter(id=company_id)

        result = []
        for company in companies_queryset:
            audits = Audit.objects.filter(company=company)

            total_audits = audits.count()
            completed = audits.filter(status='completed').count()
            avg_score = audits.filter(status='completed').aggregate(
                avg=Avg('score_percentage')
            )['avg'] or 0
            branches_count = company.branches.count()

            result.append({
                'company_id': company.id,
                'company_name': company.name,
                'total_audits': total_audits,
                'completed': completed,
                'avg_score': round(float(avg_score), 2),
                'branches_count': branches_count
            })

        return result

    @staticmethod
    def get_score_distribution(user, company_id=None):
        """
        Distribución de puntajes en rangos (para gráfico de barras).

        Returns:
            [
                {'range': '0-20', 'count': 2},
                {'range': '21-40', 'count': 5},
                {'range': '41-60', 'count': 8},
                {'range': '61-80', 'count': 15},
                {'range': '81-100', 'count': 20}
            ]
        """
        audits = StatsService._get_base_queryset(user, company_id).filter(status='completed')

        ranges = [
            ('0-20', 0, 20),
            ('21-40', 21, 40),
            ('41-60', 41, 60),
            ('61-80', 61, 80),
            ('81-100', 81, 100)
        ]

        result = []
        for range_label, min_score, max_score in ranges:
            count = audits.filter(
                score_percentage__gte=min_score,
                score_percentage__lte=max_score
            ).count()

            result.append({
                'range': range_label,
                'count': count
            })

        return result

    @staticmethod
    def get_audits_by_template(user, company_id=None):
        """
        Uso de plantillas (cuántas auditorías por plantilla).

        Returns:
            [
                {
                    'template_id': 1,
                    'template_name': 'ISO 9001',
                    'total_audits': 25,
                    'completed': 20,
                    'avg_score': 88.5
                },
                ...
            ]
        """
        audits = StatsService._get_base_queryset(user, company_id)

        # Agrupar por plantilla
        template_stats = audits.values(
            'template__id',
            'template__name'
        ).annotate(
            total_audits=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            avg_score=Avg('score_percentage', filter=Q(status='completed'))
        ).order_by('-total_audits')

        result = []
        for item in template_stats:
            result.append({
                'template_id': item['template__id'],
                'template_name': item['template__name'],
                'total_audits': item['total_audits'],
                'completed': item['completed'],
                'avg_score': round(float(item['avg_score'] or 0), 2)
            })

        return result

    @staticmethod
    def get_top_performing_branches(user, company_id=None, limit=10):
        """
        Mejores sucursales por puntaje promedio (solo completadas).

        Returns:
            [
                {
                    'branch_id': 1,
                    'branch_name': 'Sucursal Centro',
                    'company_name': 'Empresa X',
                    'total_audits': 10,
                    'avg_score': 92.5
                },
                ...
            ]
        """
        audits = StatsService._get_base_queryset(user, company_id).filter(
            status='completed',
            branch__isnull=False
        )

        # Agrupar por sucursal
        branch_stats = audits.values(
            'branch__id',
            'branch__name',
            'company__name'
        ).annotate(
            total_audits=Count('id'),
            avg_score=Avg('score_percentage')
        ).order_by('-avg_score')[:limit]

        result = []
        for item in branch_stats:
            result.append({
                'branch_id': item['branch__id'],
                'branch_name': item['branch__name'],
                'company_name': item['company__name'],
                'total_audits': item['total_audits'],
                'avg_score': round(float(item['avg_score']), 2)
            })

        return result

    @staticmethod
    def get_audits_this_period(user, company_id=None, period='month'):
        """
        Auditorías del período actual (mes o semana).

        Args:
            period: 'month', 'week', o 'day'

        Returns:
            {
                'period': 'December 2024',
                'total': 15,
                'completed': 12,
                'in_progress': 2,
                'draft': 1,
                'avg_score': 85.5,
                'audits': [...]  # Lista detallada
            }
        """
        now = timezone.now()

        if period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_label = now.strftime('%B %Y')
        elif period == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            period_label = f"Week {now.strftime('%U %Y')}"
        else:  # day
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_label = now.strftime('%Y-%m-%d')

        audits = StatsService._get_base_queryset(user, company_id).filter(
            created_at__gte=start_date
        )

        total = audits.count()
        completed = audits.filter(status='completed').count()
        in_progress = audits.filter(status='in_progress').count()
        draft = audits.filter(status='draft').count()

        avg_score = audits.filter(status='completed').aggregate(
            avg=Avg('score_percentage')
        )['avg'] or 0

        # Lista detallada
        audits_list = []
        for audit in audits.order_by('-created_at'):
            audits_list.append({
                'id': audit.id,
                'title': audit.title,
                'company_name': audit.company.name,
                'status': audit.status,
                'score_percentage': float(audit.score_percentage),
                'created_at': audit.created_at.strftime('%Y-%m-%d %H:%M')
            })

        return {
            'period': period_label,
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'draft': draft,
            'avg_score': round(float(avg_score), 2),
            'audits': audits_list
        }

    @staticmethod
    def get_category_performance(user, company_id=None):
        """
        Rendimiento por categoría de preguntas (opcional, análisis avanzado).

        Returns:
            [
                {
                    'category': 'Seguridad',
                    'total_responses': 150,
                    'avg_score': 8.5,
                    'max_possible_avg': 10
                },
                ...
            ]
        """
        audits = StatsService._get_base_queryset(user, company_id).filter(status='completed')

        # Obtener todas las respuestas de estas auditorías
        responses = AuditResponse.objects.filter(
            audit__in=audits,
            score__isnull=False
        ).select_related('question')

        # Agrupar por categoría
        categories = {}
        for response in responses:
            category = response.question.category
            if category not in categories:
                categories[category] = {
                    'total_responses': 0,
                    'total_score': 0,
                    'total_max_score': 0
                }

            categories[category]['total_responses'] += 1
            categories[category]['total_score'] += response.score
            categories[category]['total_max_score'] += response.question.max_score

        # Calcular promedios
        result = []
        for category, data in categories.items():
            avg_score = (data['total_score'] / data['total_responses']) if data['total_responses'] > 0 else 0
            max_possible_avg = (data['total_max_score'] / data['total_responses']) if data['total_responses'] > 0 else 0

            result.append({
                'category': category,
                'total_responses': data['total_responses'],
                'avg_score': round(avg_score, 2),
                'max_possible_avg': round(max_possible_avg, 2),
                'percentage': round((avg_score / max_possible_avg * 100) if max_possible_avg > 0 else 0, 2)
            })

        # Ordenar por categoría
        result.sort(key=lambda x: x['category'])

        return result
