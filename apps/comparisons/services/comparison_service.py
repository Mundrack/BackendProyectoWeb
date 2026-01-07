from django.db.models import Avg, Count, Q
from apps.audits.models import Audit
from apps.audits.services.scoring_service import ScoringService


class ComparisonService:
    """
    Servicio para manejar comparaciones entre auditorías.
    """

    @staticmethod
    def compare_audits(audit_ids, user):
        """
        Compara múltiples auditorías (hasta 5).

        Retorna:
        - audits: Lista de auditorías con sus datos
        - comparative_analysis: Análisis comparativo
        - categories_comparison: Comparación por categorías
        - trends: Tendencias si son de la misma plantilla
        """
        # Validar cantidad
        if len(audit_ids) < 2:
            raise ValueError("Debes seleccionar al menos 2 auditorías para comparar")

        if len(audit_ids) > 5:
            raise ValueError("Puedes comparar hasta 5 auditorías simultáneamente")

        # Obtener auditorías
        audits = Audit.objects.filter(
            id__in=audit_ids,
            company__owner=user,
            status='completed'
        ).select_related(
            'company', 'branch', 'template', 'assigned_to'
        ).order_by('-completed_at')

        if audits.count() != len(audit_ids):
            raise ValueError("Algunas auditorías no existen o no están completadas")

        # Verificar si son de la misma plantilla
        templates = set(audit.template_id for audit in audits)
        same_template = len(templates) == 1

        # Recopilar datos de cada auditoría
        audits_data = []
        all_categories = {}

        for audit in audits:
            # Obtener scores por categoría
            score_by_category = ScoringService.get_score_by_category(audit)

            audits_data.append({
                'id': audit.id,
                'title': audit.title,
                'company': audit.company.name,
                'branch': audit.branch.name if audit.branch else None,
                'template': audit.template.name,
                'iso_standard': audit.template.iso_standard,
                'completed_at': audit.completed_at.isoformat(),
                'total_score': float(audit.total_score),
                'max_possible_score': float(audit.max_possible_score),
                'score_percentage': float(audit.score_percentage),
                'score_by_category': score_by_category
            })

            # Agregar categorías al diccionario global
            for category, data in score_by_category.items():
                if category not in all_categories:
                    all_categories[category] = []
                all_categories[category].append({
                    'audit_id': audit.id,
                    'audit_title': audit.title,
                    'percentage': data['percentage']
                })

        # Análisis comparativo
        scores = [a['score_percentage'] for a in audits_data]

        comparative_analysis = {
            'same_template': same_template,
            'template_name': audits_data[0]['template'] if same_template else 'Mixto',
            'total_audits': len(audits_data),
            'highest_score': {
                'audit_id': audits_data[scores.index(max(scores))]['id'],
                'audit_title': audits_data[scores.index(max(scores))]['title'],
                'score': max(scores)
            },
            'lowest_score': {
                'audit_id': audits_data[scores.index(min(scores))]['id'],
                'audit_title': audits_data[scores.index(min(scores))]['title'],
                'score': min(scores)
            },
            'average_score': round(sum(scores) / len(scores), 2),
            'score_range': round(max(scores) - min(scores), 2),
            'score_variance': round(
                sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores),
                2
            )
        }

        # Comparación por categorías (solo si son de la misma plantilla)
        categories_comparison = {}
        if same_template:
            for category, category_data in all_categories.items():
                percentages = [item['percentage'] for item in category_data]

                categories_comparison[category] = {
                    'audits': category_data,
                    'average': round(sum(percentages) / len(percentages), 2),
                    'highest': max(percentages),
                    'lowest': min(percentages),
                    'range': round(max(percentages) - min(percentages), 2)
                }

        return {
            'audits': audits_data,
            'comparative_analysis': comparative_analysis,
            'categories_comparison': categories_comparison
        }

    @staticmethod
    def get_trends(audit_ids, user):
        """
        Analiza tendencias entre auditorías ordenadas cronológicamente.
        Solo funciona si son de la misma plantilla.
        """
        audits = Audit.objects.filter(
            id__in=audit_ids,
            company__owner=user,
            status='completed'
        ).order_by('completed_at')

        if audits.count() < 2:
            raise ValueError("Se necesitan al menos 2 auditorías para analizar tendencias")

        # Verificar misma plantilla
        templates = set(audit.template_id for audit in audits)
        if len(templates) > 1:
            raise ValueError("Para analizar tendencias, todas las auditorías deben usar la misma plantilla")

        # Calcular tendencia general
        scores = [float(audit.score_percentage) for audit in audits]

        # Calcular pendiente simple (primera vs última)
        trend = "improving" if scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable"

        # Calcular cambio porcentual
        change_percentage = round(((scores[-1] - scores[0]) / scores[0]) * 100, 2) if scores[0] > 0 else 0

        # Tendencias por categoría
        categories_trends = {}

        first_audit = audits.first()
        categories = ScoringService.get_score_by_category(first_audit).keys()

        for category in categories:
            category_scores = []

            for audit in audits:
                score_by_cat = ScoringService.get_score_by_category(audit)
                if category in score_by_cat:
                    category_scores.append(score_by_cat[category]['percentage'])

            if len(category_scores) >= 2:
                cat_trend = "improving" if category_scores[-1] > category_scores[0] else "declining" if category_scores[-1] < category_scores[0] else "stable"
                cat_change = round(((category_scores[-1] - category_scores[0]) / category_scores[0]) * 100, 2) if category_scores[0] > 0 else 0

                categories_trends[category] = {
                    'scores': category_scores,
                    'trend': cat_trend,
                    'change_percentage': cat_change
                }

        return {
            'overall_trend': trend,
            'change_percentage': change_percentage,
            'scores_timeline': scores,
            'categories_trends': categories_trends,
            'audits_count': len(scores)
        }
