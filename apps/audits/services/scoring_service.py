from django.db.models import Avg, Sum, Count, Q
from apps.audits.models import Audit, AuditResponse


class ScoringService:
    """
    Servicio para cálculos de scores y estadísticas de auditorías.
    """

    @staticmethod
    def get_score_by_category(audit):
        """
        Obtiene los scores agrupados por categoría.
        Retorna dict con info por cada categoría.
        """
        responses = audit.responses.select_related('question').all()

        categories = {}
        for response in responses:
            category = response.question.category

            if category not in categories:
                categories[category] = {
                    'total_score': 0,
                    'max_score': 0,
                    'answered': 0,
                    'total_questions': 0
                }

            categories[category]['total_questions'] += 1
            categories[category]['max_score'] += response.question.max_score

            if response.score is not None:
                categories[category]['total_score'] += response.score
                categories[category]['answered'] += 1

        # Calcular porcentajes
        for category in categories:
            data = categories[category]
            if data['max_score'] > 0:
                data['percentage'] = round(
                    (data['total_score'] / data['max_score']) * 100,
                    2
                )
            else:
                data['percentage'] = 0

            # Promedio por pregunta
            if data['answered'] > 0:
                data['average_score'] = round(
                    data['total_score'] / data['answered'],
                    2
                )
            else:
                data['average_score'] = 0

        return categories

    @staticmethod
    def get_audit_summary(audit):
        """
        Genera un resumen completo de la auditoría con estadísticas.
        """
        score_by_category = ScoringService.get_score_by_category(audit)

        return {
            'audit_id': audit.id,
            'title': audit.title,
            'status': audit.status,
            'total_score': float(audit.total_score),
            'max_possible_score': float(audit.max_possible_score),
            'score_percentage': float(audit.score_percentage),
            'total_questions': audit.total_questions_count,
            'answered_questions': audit.answered_questions_count,
            'progress_percentage': audit.progress_percentage,
            'categories': score_by_category,
            'started_at': audit.started_at,
            'completed_at': audit.completed_at,
        }
