from apps.comparisons.models import Recommendation


class RecommendationService:
    """
    Servicio para generar recomendaciones automáticas.
    """

    # Umbrales de score para priorización
    THRESHOLDS = {
        'high': 60,    # Menos de 60% = prioridad alta
        'medium': 75,  # Entre 60-75% = prioridad media
        'low': 85      # Entre 75-85% = prioridad baja
        # Más de 85% = sin recomendación o felicitación
    }

    @staticmethod
    def generate_recommendations(audit):
        """
        Genera recomendaciones automáticas basadas en los scores.

        Analiza:
        - Score general de la auditoría
        - Scores por categoría
        - Preguntas con scores bajos

        Retorna lista de recomendaciones creadas.
        """
        from apps.audits.services.scoring_service import ScoringService

        # Eliminar recomendaciones automáticas previas
        Recommendation.objects.filter(
            audit=audit,
            is_auto_generated=True
        ).delete()

        recommendations = []

        # Obtener scores por categoría
        score_by_category = ScoringService.get_score_by_category(audit)

        # Generar recomendaciones por categoría
        for category, data in score_by_category.items():
            percentage = data['percentage']

            # Determinar prioridad y generar recomendación
            if percentage < RecommendationService.THRESHOLDS['high']:
                priority = 'high'
                recommendation_text = (
                    f"La categoría '{category}' obtuvo {percentage:.1f}% y requiere atención inmediata. "
                    f"Se recomienda: revisar todos los procesos relacionados, establecer un plan de acción "
                    f"correctivo, capacitar al personal responsable y programar seguimiento en 30 días."
                )

            elif percentage < RecommendationService.THRESHOLDS['medium']:
                priority = 'medium'
                recommendation_text = (
                    f"La categoría '{category}' obtuvo {percentage:.1f}% y debe ser mejorada. "
                    f"Se recomienda: documentar mejor los procesos, reforzar controles existentes "
                    f"y realizar revisiones periódicas."
                )

            elif percentage < RecommendationService.THRESHOLDS['low']:
                priority = 'low'
                recommendation_text = (
                    f"La categoría '{category}' obtuvo {percentage:.1f}% y puede optimizarse. "
                    f"Se recomienda: identificar oportunidades de mejora continua y mantener "
                    f"las buenas prácticas actuales."
                )

            else:
                # Score excelente, generar felicitación
                priority = 'low'
                recommendation_text = (
                    f"¡Excelente desempeño! La categoría '{category}' obtuvo {percentage:.1f}%. "
                    f"Se recomienda: mantener los estándares actuales y documentar las mejores "
                    f"prácticas para replicarlas."
                )

            # Crear recomendación
            recommendation = Recommendation.objects.create(
                audit=audit,
                category=category,
                recommendation_text=recommendation_text,
                priority=priority,
                is_auto_generated=True
            )

            recommendations.append(recommendation)

        # Recomendación general basada en score total
        total_percentage = float(audit.score_percentage)

        if total_percentage < RecommendationService.THRESHOLDS['high']:
            general_text = (
                f"Score general de {total_percentage:.1f}% indica necesidad de mejora significativa. "
                f"Se recomienda: establecer un comité de mejora, asignar recursos dedicados, "
                f"realizar auditoría de seguimiento en 60 días."
            )
            general_priority = 'high'

        elif total_percentage < RecommendationService.THRESHOLDS['medium']:
            general_text = (
                f"Score general de {total_percentage:.1f}% es aceptable pero mejorable. "
                f"Se recomienda: enfocarse en las áreas con menor puntaje y establecer "
                f"indicadores de seguimiento."
            )
            general_priority = 'medium'

        elif total_percentage < RecommendationService.THRESHOLDS['low']:
            general_text = (
                f"Score general de {total_percentage:.1f}% es bueno. "
                f"Se recomienda: mantener el nivel actual y buscar oportunidades de excelencia "
                f"en áreas específicas."
            )
            general_priority = 'low'

        else:
            general_text = (
                f"¡Excelente score general de {total_percentage:.1f}%! "
                f"Se recomienda: mantener los estándares, documentar mejores prácticas y "
                f"servir como referencia para otras áreas."
            )
            general_priority = 'low'

        general_recommendation = Recommendation.objects.create(
            audit=audit,
            category='General',
            recommendation_text=general_text,
            priority=general_priority,
            is_auto_generated=True
        )

        recommendations.append(general_recommendation)

        return recommendations

    @staticmethod
    def get_recommendations_summary(audit):
        """
        Obtiene resumen de recomendaciones de una auditoría.
        """
        recommendations = audit.recommendations.all()

        return {
            'total': recommendations.count(),
            'high_priority': recommendations.filter(priority='high').count(),
            'medium_priority': recommendations.filter(priority='medium').count(),
            'low_priority': recommendations.filter(priority='low').count(),
            'auto_generated': recommendations.filter(is_auto_generated=True).count(),
            'manual': recommendations.filter(is_auto_generated=False).count()
        }
