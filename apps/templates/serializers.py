from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AuditTemplate, TemplateQuestion

User = get_user_model()


class TemplateQuestionSerializer(serializers.ModelSerializer):
    """Serializer para Preguntas de Plantilla"""

    class Meta:
        model = TemplateQuestion
        fields = [
            'id', 'template', 'category', 'question_text',
            'order_num', 'max_score', 'is_required',
            'help_text', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_order_num(self, value):
        """Validar que el order_num sea positivo"""
        if value < 1:
            raise serializers.ValidationError(
                "El orden debe ser un número positivo mayor a 0"
            )
        return value

    def validate_max_score(self, value):
        """Validar que el max_score esté entre 1 y 10"""
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                "El puntaje máximo debe estar entre 1 y 10"
            )
        return value

    def validate(self, attrs):
        """Validar que no haya preguntas duplicadas con el mismo orden"""
        template = attrs.get('template')
        order_num = attrs.get('order_num')

        # Si es actualización, excluir la pregunta actual
        instance_id = self.instance.id if self.instance else None

        existing = TemplateQuestion.objects.filter(
            template=template,
            order_num=order_num
        ).exclude(id=instance_id)

        if existing.exists():
            raise serializers.ValidationError({
                'order_num': f'Ya existe una pregunta con el orden {order_num} en esta plantilla'
            })

        return attrs


class TemplateQuestionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar preguntas"""

    class Meta:
        model = TemplateQuestion
        fields = [
            'id', 'category', 'question_text',
            'order_num', 'max_score', 'is_required'
        ]


class AuditTemplateSerializer(serializers.ModelSerializer):
    """Serializer completo para Plantillas de Auditoría"""

    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    questions = TemplateQuestionListSerializer(
        many=True,
        read_only=True
    )
    total_questions = serializers.SerializerMethodField()
    max_possible_score = serializers.SerializerMethodField()
    categories_list = serializers.SerializerMethodField()

    class Meta:
        model = AuditTemplate
        fields = [
            'id', 'name', 'iso_standard', 'description',
            'created_by', 'created_by_name', 'is_active', 'version',
            'questions', 'total_questions', 'max_possible_score',
            'categories_list', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_total_questions(self, obj):
        """Obtener total de preguntas usando la propiedad del modelo"""
        return obj.total_questions

    def get_max_possible_score(self, obj):
        """Obtener puntaje máximo usando la propiedad del modelo"""
        return obj.max_possible_score

    def get_categories_list(self, obj):
        """Obtener lista de categorías únicas"""
        return list(obj.categories)

    def create(self, validated_data):
        """Asignar automáticamente el created_by del request"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AuditTemplateListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar plantillas"""

    total_questions = serializers.SerializerMethodField()
    max_possible_score = serializers.SerializerMethodField()

    class Meta:
        model = AuditTemplate
        fields = [
            'id', 'name', 'iso_standard', 'description',
            'is_active', 'version', 'total_questions',
            'max_possible_score', 'created_at'
        ]

    def get_total_questions(self, obj):
        """Obtener total de preguntas usando la propiedad del modelo"""
        return obj.total_questions

    def get_max_possible_score(self, obj):
        """Obtener puntaje máximo usando la propiedad del modelo"""
        return obj.max_possible_score


class TemplateQuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear múltiples preguntas a la vez"""

    class Meta:
        model = TemplateQuestion
        fields = [
            'category', 'question_text', 'order_num',
            'max_score', 'is_required', 'help_text'
        ]


class TemplateBulkCreateSerializer(serializers.Serializer):
    """Serializer para crear plantilla con todas sus preguntas"""

    name = serializers.CharField(max_length=200)
    iso_standard = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)
    version = serializers.IntegerField(default=1, min_value=1)
    questions = TemplateQuestionCreateSerializer(many=True)

    def validate_questions(self, value):
        """Validar que haya al menos una pregunta"""
        if not value:
            raise serializers.ValidationError(
                "Debe incluir al menos una pregunta"
            )

        # Validar que no haya órdenes duplicados
        orders = [q['order_num'] for q in value]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError(
                "No puede haber preguntas con el mismo número de orden"
            )

        return value

    def create(self, validated_data):
        """Crear plantilla con todas sus preguntas"""
        questions_data = validated_data.pop('questions')

        # Crear la plantilla
        template = AuditTemplate.objects.create(
            created_by=self.context['request'].user,
            **validated_data
        )

        # Crear todas las preguntas
        questions = [
            TemplateQuestion(template=template, **question_data)
            for question_data in questions_data
        ]
        TemplateQuestion.objects.bulk_create(questions)

        return template
