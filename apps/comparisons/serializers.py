from rest_framework import serializers
from .models import Comparison, ComparisonAudit, Recommendation
from apps.audits.serializers import AuditListSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer para Recomendaciones"""

    audit_title = serializers.CharField(
        source='audit.title',
        read_only=True
    )
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Recommendation
        fields = [
            'id', 'audit', 'audit_title', 'category',
            'recommendation_text', 'priority', 'is_auto_generated',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RecommendationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear recomendaciones manuales"""

    class Meta:
        model = Recommendation
        fields = [
            'audit', 'category', 'recommendation_text', 'priority'
        ]

    def create(self, validated_data):
        # Establecer created_by y is_auto_generated
        validated_data['created_by'] = self.context['request'].user
        validated_data['is_auto_generated'] = False
        return super().create(validated_data)


class ComparisonAuditSerializer(serializers.ModelSerializer):
    """Serializer para auditorías en comparación"""

    audit_detail = AuditListSerializer(source='audit', read_only=True)

    class Meta:
        model = ComparisonAudit
        fields = ['id', 'audit', 'audit_detail', 'order']


class ComparisonSerializer(serializers.ModelSerializer):
    """Serializer completo para Comparaciones"""

    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    audits_detail = ComparisonAuditSerializer(
        source='comparisonaudit_set',
        many=True,
        read_only=True
    )
    audit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comparison
        fields = [
            'id', 'name', 'description', 'created_by',
            'created_by_name', 'audits_detail', 'audit_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ComparisonCreateSerializer(serializers.Serializer):
    """Serializer para crear comparaciones"""

    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    audit_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=5,
        write_only=True
    )

    def validate_audit_ids(self, value):
        """Validar que haya entre 2 y 5 auditorías"""
        if len(value) < 2:
            raise serializers.ValidationError(
                "Debes seleccionar al menos 2 auditorías"
            )
        if len(value) > 5:
            raise serializers.ValidationError(
                "Puedes comparar hasta 5 auditorías"
            )

        # Validar que no haya duplicados
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "No puede haber auditorías duplicadas"
            )

        return value

    def create(self, validated_data):
        """Crear comparación con auditorías"""
        from apps.audits.models import Audit

        audit_ids = validated_data.pop('audit_ids')
        user = self.context['request'].user

        # Validar que todas las auditorías existan y estén completadas
        audits = []
        for audit_id in audit_ids:
            try:
                audit = Audit.objects.get(id=audit_id)
            except Audit.DoesNotExist:
                raise serializers.ValidationError({
                    'audit_ids': f'La auditoría con ID {audit_id} no existe. Por favor usa IDs de auditorías válidas.'
                })

            # Verificar que la auditoría esté completada
            if audit.status != 'completed':
                raise serializers.ValidationError({
                    'audit_ids': f'La auditoría "{audit.title}" (ID: {audit_id}) no está completada. Solo puedes comparar auditorías completadas.'
                })

            # Verificar permisos del usuario
            if hasattr(user, 'owner_profile'):
                if audit.company.owner != user:
                    raise serializers.ValidationError({
                        'audit_ids': f'No tienes permiso para acceder a la auditoría con ID {audit_id}.'
                    })

            audits.append(audit)

        # Crear la comparación
        comparison = Comparison.objects.create(
            created_by=user,
            **validated_data
        )

        # Asociar auditorías en orden
        for order, audit in enumerate(audits, start=1):
            ComparisonAudit.objects.create(
                comparison=comparison,
                audit=audit,
                order=order
            )

        return comparison


class CompareAuditsSerializer(serializers.Serializer):
    """Serializer para comparar auditorías sin guardar"""

    audit_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=5
    )

    def validate_audit_ids(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "Debes seleccionar al menos 2 auditorías"
            )
        if len(value) > 5:
            raise serializers.ValidationError(
                "Puedes comparar hasta 5 auditorías"
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "No puede haber auditorías duplicadas"
            )
        return value
