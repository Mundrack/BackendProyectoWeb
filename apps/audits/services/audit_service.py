from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.audits.models import Audit, AuditResponse
from apps.templates.models import TemplateQuestion


class AuditService:
    """
    Servicio para manejar la lógica de negocio de auditorías.
    Contiene los métodos para gestionar el ciclo de vida completo.
    """

    @staticmethod
    def start_audit(audit_id, user):
        """
        Inicia una auditoría cambiando su estado a 'in_progress'.
        Solo puede iniciarse si está en estado 'draft'.
        """
        try:
            audit = Audit.objects.get(id=audit_id)

            # Validar que el usuario pueda iniciarla
            if audit.assigned_to != user and audit.created_by != user:
                raise ValidationError(
                    "No tienes permiso para iniciar esta auditoría"
                )

            # Validar estado
            if audit.status != 'draft':
                raise ValidationError(
                    "Solo se pueden iniciar auditorías en estado borrador"
                )

            # Iniciar
            audit.status = 'in_progress'
            audit.started_at = timezone.now()
            audit.save()

            return audit

        except Audit.DoesNotExist:
            raise ValidationError("Auditoría no encontrada")

    @staticmethod
    @transaction.atomic
    def save_response(audit_id, question_id, score, notes, evidence_file, user, response_type=None):
        """
        Guarda o actualiza una respuesta a una pregunta de auditoría.
        Recalcula el score automáticamente.
        """
        try:
            audit = Audit.objects.select_related('template').get(id=audit_id)
            question = TemplateQuestion.objects.get(id=question_id)

            # Validar permisos
            if audit.assigned_to != user and audit.created_by != user:
                raise ValidationError(
                    "No tienes permiso para responder esta auditoría"
                )

            # Validar estado
            if audit.status not in ['draft', 'in_progress']:
                raise ValidationError(
                    "No se pueden guardar respuestas en una auditoría completada o cancelada"
                )

            # Validar que la pregunta pertenece a la plantilla
            if question.template != audit.template:
                raise ValidationError(
                    "La pregunta no pertenece a esta auditoría"
                )

            # Validar score
            if score is not None:
                if score < 0 or score > question.max_score:
                    raise ValidationError(
                        f"El puntaje debe estar entre 0 y {question.max_score}"
                    )

            # Crear o actualizar respuesta
            response, created = AuditResponse.objects.update_or_create(
                audit=audit,
                question=question,
                defaults={
                    'response_type': response_type,
                    'score': score,
                    'notes': notes,
                    'evidence_file': evidence_file or ''
                }
            )

            # Recalcular score de la auditoría
            audit.calculate_score()

            return response

        except (Audit.DoesNotExist, TemplateQuestion.DoesNotExist):
            raise ValidationError("Auditoría o pregunta no encontrada")

    @staticmethod
    @transaction.atomic
    def complete_audit(audit_id, user):
        """
        Completa una auditoría verificando que todas las preguntas
        obligatorias estén respondidas.
        """
        try:
            audit = Audit.objects.select_related('template').get(id=audit_id)

            # Validar permisos
            if audit.assigned_to != user and audit.created_by != user:
                raise ValidationError(
                    "No tienes permiso para completar esta auditoría"
                )

            # Validar estado
            if audit.status != 'in_progress':
                raise ValidationError(
                    "Solo se pueden completar auditorías en progreso"
                )

            # Validar que todas las preguntas obligatorias estén respondidas
            # Una pregunta está respondida si existe un registro de respuesta,
            # independientemente de si tiene score o no (puede ser 'na')
            required_questions = audit.template.questions.filter(
                is_required=True
            ).count()

            answered_required = audit.responses.filter(
                question__is_required=True
            ).count()

            if answered_required < required_questions:
                missing = required_questions - answered_required
                raise ValidationError(
                    f"Faltan {missing} preguntas obligatorias por responder"
                )

            # Calcular score final
            audit.calculate_score()

            # Completar
            audit.status = 'completed'
            audit.completed_at = timezone.now()
            audit.save()

            return audit

        except Audit.DoesNotExist:
            raise ValidationError("Auditoría no encontrada")

    @staticmethod
    def cancel_audit(audit_id, user):
        """
        Cancela una auditoría.
        Solo puede cancelarse si no está completada.
        """
        try:
            audit = Audit.objects.get(id=audit_id)

            # Validar permisos
            if audit.created_by != user:
                raise ValidationError(
                    "Solo el creador puede cancelar la auditoría"
                )

            # Validar estado
            if audit.status == 'completed':
                raise ValidationError(
                    "No se puede cancelar una auditoría completada"
                )

            # Cancelar
            audit.status = 'cancelled'
            audit.save()

            return audit

        except Audit.DoesNotExist:
            raise ValidationError("Auditoría no encontrada")
