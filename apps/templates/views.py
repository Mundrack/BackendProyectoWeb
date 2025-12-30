from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from .models import AuditTemplate, TemplateQuestion
from .serializers import (
    AuditTemplateSerializer, AuditTemplateListSerializer,
    TemplateQuestionSerializer, TemplateQuestionListSerializer,
    TemplateBulkCreateSerializer
)
from apps.authentication.permissions import IsOwner


class AuditTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Plantillas de Auditoría.

    Lista, crea, actualiza y elimina plantillas.
    Solo los owners pueden crear/editar plantillas.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar plantillas según el tipo de usuario:
        - Owners: todas las plantillas activas + sus propias plantillas
        - Employees: solo plantillas activas
        """
        user = self.request.user

        queryset = AuditTemplate.objects.select_related('created_by')

        if user.user_type == 'owner':
            # Owners ven plantillas activas + las que ellos crearon
            queryset = queryset.filter(
                Q(is_active=True) | Q(created_by=user)
            )
        else:
            # Employees solo ven plantillas activas
            queryset = queryset.filter(is_active=True)

        return queryset.distinct()

    def get_serializer_class(self):
        """Usar serializer diferente para list vs detail"""
        if self.action == 'list':
            return AuditTemplateListSerializer
        elif self.action == 'bulk_create':
            return TemplateBulkCreateSerializer
        return AuditTemplateSerializer

    def get_permissions(self):
        """
        Permisos específicos por acción:
        - create/update/delete: solo owners
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'bulk_create']:
            return [IsAuthenticated(), IsOwner()]
        return super().get_permissions()

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Endpoint personalizado: POST /api/templates/bulk_create/
        Crear plantilla con todas sus preguntas en una sola petición
        """
        serializer = TemplateBulkCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        template = serializer.save()

        # Retornar la plantilla creada con todas sus preguntas
        output_serializer = AuditTemplateSerializer(template)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """
        Endpoint personalizado: GET /api/templates/{id}/questions/
        Obtener todas las preguntas de una plantilla
        """
        template = self.get_object()
        questions = template.questions.all()
        serializer = TemplateQuestionSerializer(questions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def categories(self, request, pk=None):
        """
        Endpoint personalizado: GET /api/templates/{id}/categories/
        Obtener preguntas agrupadas por categoría
        """
        template = self.get_object()
        questions = template.questions.all()

        # Agrupar por categoría
        categories_dict = {}
        for question in questions:
            if question.category not in categories_dict:
                categories_dict[question.category] = []

            categories_dict[question.category].append({
                'id': question.id,
                'question_text': question.question_text,
                'order_num': question.order_num,
                'max_score': question.max_score,
                'is_required': question.is_required,
                'help_text': question.help_text
            })

        # Convertir a lista
        categories_list = [
            {
                'category': category,
                'questions': questions_list,
                'total_questions': len(questions_list),
                'max_score': sum(q['max_score'] for q in questions_list)
            }
            for category, questions_list in categories_dict.items()
        ]

        return Response({
            'template_id': template.id,
            'template_name': template.name,
            'categories': categories_list
        })

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Endpoint personalizado: POST /api/templates/{id}/duplicate/
        Duplicar una plantilla con todas sus preguntas
        """
        original_template = self.get_object()

        # Obtener nuevo nombre del request
        new_name = request.data.get('name', f"{original_template.name} (Copia)")

        # Crear nueva plantilla
        new_template = AuditTemplate.objects.create(
            name=new_name,
            iso_standard=original_template.iso_standard,
            description=original_template.description,
            created_by=request.user,
            is_active=original_template.is_active,
            version=1
        )

        # Copiar todas las preguntas
        original_questions = original_template.questions.all()
        new_questions = [
            TemplateQuestion(
                template=new_template,
                category=q.category,
                question_text=q.question_text,
                order_num=q.order_num,
                max_score=q.max_score,
                is_required=q.is_required,
                help_text=q.help_text
            )
            for q in original_questions
        ]
        TemplateQuestion.objects.bulk_create(new_questions)

        # Retornar la nueva plantilla
        serializer = AuditTemplateSerializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TemplateQuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Preguntas de Plantilla.

    Permite CRUD de preguntas individuales.
    Solo los owners pueden crear/editar preguntas.
    """

    serializer_class = TemplateQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar preguntas según permisos del usuario"""
        user = self.request.user

        if user.user_type == 'owner':
            # Owners ven preguntas de plantillas activas + sus propias plantillas
            return TemplateQuestion.objects.filter(
                Q(template__is_active=True) |
                Q(template__created_by=user)
            ).select_related('template', 'template__created_by')
        else:
            # Employees solo ven preguntas de plantillas activas
            return TemplateQuestion.objects.filter(
                template__is_active=True
            ).select_related('template')

    def get_permissions(self):
        """Permisos: solo owners pueden modificar"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Validar que el owner pueda crear preguntas en su plantilla"""
        template_id = request.data.get('template')

        try:
            template = AuditTemplate.objects.get(id=template_id)
            if template.created_by != request.user:
                return Response(
                    {
                        'error': 'No tienes permiso para agregar preguntas a esta plantilla',
                        'details': {
                            'template': ['Solo el creador puede agregar preguntas']
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except AuditTemplate.DoesNotExist:
            return Response(
                {
                    'error': 'Plantilla no encontrada',
                    'details': {
                        'template': ['La plantilla especificada no existe']
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Endpoint personalizado: POST /api/questions/reorder/
        Reordenar preguntas de una plantilla

        Request body:
        {
            "template_id": 1,
            "questions": [
                {"id": 1, "order_num": 1},
                {"id": 2, "order_num": 2},
                ...
            ]
        }
        """
        template_id = request.data.get('template_id')
        questions_data = request.data.get('questions', [])

        if not template_id or not questions_data:
            return Response(
                {
                    'error': 'Faltan datos requeridos',
                    'details': {
                        'non_field_errors': ['Se requiere template_id y questions']
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            template = AuditTemplate.objects.get(id=template_id)

            # Validar permisos
            if template.created_by != request.user:
                return Response(
                    {
                        'error': 'No tienes permiso para reordenar esta plantilla'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Actualizar órdenes
            for item in questions_data:
                TemplateQuestion.objects.filter(
                    id=item['id'],
                    template=template
                ).update(order_num=item['order_num'])

            return Response({
                'message': 'Preguntas reordenadas exitosamente'
            })

        except AuditTemplate.DoesNotExist:
            return Response(
                {
                    'error': 'Plantilla no encontrada'
                },
                status=status.HTTP_404_NOT_FOUND
            )
