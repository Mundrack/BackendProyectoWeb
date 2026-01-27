from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Audit, AuditResponse
from apps.companies.serializers import CompanySerializer, BranchSerializer
from apps.templates.serializers import AuditTemplateSerializer, TemplateQuestionSerializer

User = get_user_model()


class AuditResponseSerializer(serializers.ModelSerializer):
    """Serializer para Respuestas de Auditoría"""

    question_text = serializers.CharField(
        source='question.question_text',
        read_only=True
    )
    category = serializers.CharField(
        source='question.category',
        read_only=True
    )
    order_num = serializers.IntegerField(
        source='question.order_num',
        read_only=True
    )
    max_score = serializers.IntegerField(
        source='question.max_score',
        read_only=True
    )
    help_text = serializers.CharField(
        source='question.help_text',
        read_only=True
    )

    class Meta:
        model = AuditResponse
        fields = [
            'id', 'audit', 'question', 'question_text',
            'category', 'order_num', 'max_score', 'help_text',
            'score', 'notes', 'evidence_file', 'responded_at'
        ]
        read_only_fields = ['id', 'responded_at']

    def validate_score(self, value):
        """Validar que el score no exceda el máximo de la pregunta"""
        if value is not None:
            question = self.initial_data.get('question')
            if question:
                from apps.templates.models import TemplateQuestion
                try:
                    q = TemplateQuestion.objects.get(id=question)
                    if value > q.max_score:
                        raise serializers.ValidationError(
                            f'El puntaje no puede exceder {q.max_score}'
                        )
                except TemplateQuestion.DoesNotExist:
                    pass
        return value


class AuditResponseCreateSerializer(serializers.Serializer):
    """Serializer simplificado para crear/actualizar respuestas"""

    question_id = serializers.IntegerField()
    
    # Aceptar tanto 'response' (tipo) como 'score' (número)
    response = serializers.ChoiceField(
        choices=['yes', 'no', 'partial', 'na'],
        required=False,
        allow_null=True
    )
    score = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=10
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True
    )
    evidence_file = serializers.CharField(
        required=False,
        allow_blank=True
    )

    def validate(self, attrs):
        """Validar que se proporcione response o score"""
        response = attrs.get('response')
        score = attrs.get('score')
        
        # Si no se proporciona ni response ni score, es válido (permite guardar solo notas)
        # Si se proporciona response, convertirlo a score
        if response is not None:
            # Obtener la pregunta para conocer el max_score
            question_id = attrs.get('question_id')
            if question_id:
                from apps.templates.models import TemplateQuestion
                try:
                    question = TemplateQuestion.objects.get(id=question_id)
                    max_score = question.max_score
                    
                    # Convertir response a score
                    response_to_score = {
                        'yes': max_score,           # 100% del puntaje
                        'partial': max_score * 0.5, # 50% del puntaje
                        'no': 0,                    # 0% del puntaje
                        'na': None,                 # No aplica = sin puntaje
                    }
                    
                    attrs['score'] = response_to_score.get(response)
                except TemplateQuestion.DoesNotExist:
                    pass
        
        return attrs



class AuditListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar auditorías"""

    company_name = serializers.CharField(
        source='company.name',
        read_only=True
    )
    branch_name = serializers.CharField(
        source='branch.name',
        read_only=True,
        allow_null=True
    )
    template_name = serializers.CharField(
        source='template.name',
        read_only=True
    )
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name',
        read_only=True
    )
    progress = serializers.FloatField(
        source='progress_percentage',
        read_only=True
    )

    class Meta:
        model = Audit
        fields = [
            'id', 'title', 'template', 'company_name', 'branch_name',
            'template_name', 'assigned_to_name', 'status',
            'scheduled_date', 'score_percentage', 'progress',
            'created_at', 'completed_at'
        ]


class AuditDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de auditoría"""

    company = CompanySerializer(read_only=True)
    branch = BranchSerializer(read_only=True)
    template = AuditTemplateSerializer(read_only=True)
    assigned_to = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    progress = serializers.FloatField(
        source='progress_percentage',
        read_only=True
    )
    answered_questions = serializers.IntegerField(
        source='answered_questions_count',
        read_only=True
    )
    total_questions = serializers.IntegerField(
        source='total_questions_count',
        read_only=True
    )

    class Meta:
        model = Audit
        fields = [
            'id', 'title', 'template', 'company', 'branch',
            'assigned_to', 'created_by', 'status',
            'scheduled_date', 'started_at', 'completed_at',
            'total_score', 'max_possible_score', 'score_percentage',
            'progress', 'answered_questions', 'total_questions',
            'notes', 'created_at', 'updated_at'
        ]

    def get_assigned_to(self, obj):
        return {
            'id': obj.assigned_to.id,
            'full_name': obj.assigned_to.get_full_name(),
            'email': obj.assigned_to.email
        }

    def get_created_by(self, obj):
        return {
            'id': obj.created_by.id,
            'full_name': obj.created_by.get_full_name(),
            'email': obj.created_by.email
        }


class AuditCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear auditorías"""

    class Meta:
        model = Audit
        fields = [
            'title', 'template', 'company', 'branch',
            'assigned_to', 'scheduled_date', 'notes'
        ]

    def validate_assigned_to(self, value):
        """Validar que el asignado sea tipo employee"""
        if value.user_type != 'employee':
            raise serializers.ValidationError(
                "El auditor debe ser un usuario de tipo 'employee'"
            )
        return value

    def validate(self, attrs):
        """Validar que la sucursal pertenezca a la empresa"""
        branch = attrs.get('branch')
        company = attrs.get('company')

        if branch and branch.company != company:
            raise serializers.ValidationError({
                'branch': 'La sucursal no pertenece a la empresa seleccionada'
            })

        return attrs

    def create(self, validated_data):
        # Agregar created_by del request
        validated_data['created_by'] = self.context['request'].user

        # Calcular max_possible_score desde la plantilla
        template = validated_data['template']
        validated_data['max_possible_score'] = template.max_possible_score

        return super().create(validated_data)
