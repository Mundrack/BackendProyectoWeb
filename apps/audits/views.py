from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Audit, AuditResponse
from .serializers import (
    AuditListSerializer, AuditDetailSerializer, AuditCreateSerializer,
    AuditResponseSerializer, AuditResponseCreateSerializer
)
from .services.audit_service import AuditService
from .services.scoring_service import ScoringService
from apps.authentication.permissions import IsOwner


class AuditViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Auditorías (CORE del sistema).

    Permite CRUD completo y acciones especiales:
    - start: Iniciar auditoría
    - respond: Guardar respuesta a pregunta
    - complete: Completar auditoría
    - cancel: Cancelar auditoría
    - report: Generar reporte
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar auditorías según el tipo de usuario:
        - Owners: auditorías de sus empresas o que crearon
        - Employees: auditorías donde están asignados
        """
        user = self.request.user

        queryset = Audit.objects.select_related(
            'template', 'company', 'branch',
            'assigned_to', 'created_by'
        )

        if user.user_type == 'owner':
            # Owners ven auditorías de sus empresas O que ellos crearon
            queryset = queryset.filter(
                Q(company__owner=user) | Q(created_by=user)
            )
        else:
            # Employees ven auditorías donde están asignados
            queryset = queryset.filter(assigned_to=user)

        # Filtros opcionales por query params
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        company_filter = self.request.query_params.get('company')
        if company_filter:
            queryset = queryset.filter(company_id=company_filter)

        return queryset.distinct().order_by('-created_at')

    def get_serializer_class(self):
        """Usar serializer diferente según la acción"""
        if self.action == 'list':
            return AuditListSerializer
        elif self.action == 'create':
            return AuditCreateSerializer
        return AuditDetailSerializer

    def get_permissions(self):
        """Permisos: solo owners pueden crear auditorías"""
        if self.action in ['create']:
            return [IsAuthenticated(), IsOwner()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        POST /api/audits/{id}/start/
        Inicia una auditoría (draft → in_progress)
        """
        audit = self.get_object()

        try:
            audit = AuditService.start_audit(audit.id, request.user)
            serializer = AuditDetailSerializer(audit)

            return Response({
                'message': 'Auditoría iniciada exitosamente',
                'audit': serializer.data
            })

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """
        GET /api/audits/{id}/questions/
        Obtiene todas las preguntas con sus respuestas actuales
        """
        audit = self.get_object()
        template_questions = audit.template.questions.all()

        # Obtener respuestas existentes
        responses_dict = {
            r.question_id: r
            for r in audit.responses.all()
        }

        questions_data = []
        for question in template_questions:
            response = responses_dict.get(question.id)

            questions_data.append({
                'id': question.id,
                'category': question.category,
                'question_text': question.question_text,
                'order_num': question.order_num,
                'max_score': question.max_score,
                'is_required': question.is_required,
                'help_text': question.help_text,
                'response': {
                    'score': response.score if response else None,
                    'notes': response.notes if response else '',
                    'evidence_file': response.evidence_file if response else '',
                    'responded_at': response.responded_at if response else None
                } if response else None
            })

        return Response({
            'audit_id': audit.id,
            'audit_title': audit.title,
            'status': audit.status,
            'total_questions': len(questions_data),
            'answered': audit.answered_questions_count,
            'progress': audit.progress_percentage,
            'questions': questions_data
        })

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """
        POST /api/audits/{id}/respond/
        Guarda una respuesta a una pregunta

        Body: {
            "question_id": 1,
            "score": 4,
            "notes": "Cumple parcialmente",
            "evidence_file": "https://..."
        }
        """
        audit = self.get_object()
        serializer = AuditResponseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            response = AuditService.save_response(
                audit_id=audit.id,
                question_id=serializer.validated_data['question_id'],
                score=serializer.validated_data.get('score'),
                notes=serializer.validated_data.get('notes', ''),
                evidence_file=serializer.validated_data.get('evidence_file', ''),
                user=request.user
            )

            # Refrescar audit para obtener scores actualizados
            audit.refresh_from_db()

            return Response({
                'message': 'Respuesta guardada exitosamente',
                'response': AuditResponseSerializer(response).data,
                'audit_progress': {
                    'answered': audit.answered_questions_count,
                    'total': audit.total_questions_count,
                    'percentage': audit.progress_percentage,
                    'current_score': float(audit.total_score),
                    'max_score': float(audit.max_possible_score),
                    'score_percentage': float(audit.score_percentage)
                }
            })

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        POST /api/audits/{id}/complete/
        Completa la auditoría (in_progress → completed)
        """
        audit = self.get_object()

        try:
            audit = AuditService.complete_audit(audit.id, request.user)

            # Generar resumen
            summary = ScoringService.get_audit_summary(audit)

            return Response({
                'message': 'Auditoría completada exitosamente',
                'summary': summary
            })

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        POST /api/audits/{id}/cancel/
        Cancela la auditoría
        """
        audit = self.get_object()

        try:
            audit = AuditService.cancel_audit(audit.id, request.user)

            return Response({
                'message': 'Auditoría cancelada exitosamente',
                'audit': AuditDetailSerializer(audit).data
            })

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """
        GET /api/audits/{id}/report/
        Genera reporte completo de la auditoría
        """
        audit = self.get_object()

        # Generar resumen completo
        summary = ScoringService.get_audit_summary(audit)

        # Agregar información adicional
        summary['company'] = {
            'name': audit.company.name,
            'address': audit.company.address
        }

        if audit.branch:
            summary['branch'] = {
                'name': audit.branch.name,
                'address': audit.branch.address
            }

        summary['auditor'] = {
            'name': audit.assigned_to.get_full_name(),
            'email': audit.assigned_to.email
        }

        return Response(summary)
