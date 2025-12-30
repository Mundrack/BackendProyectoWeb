from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company, Branch, Department

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer para Departamentos"""

    branch_name = serializers.CharField(
        source='branch.name',
        read_only=True
    )
    company_name = serializers.CharField(
        source='branch.company.name',
        read_only=True
    )

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'description', 'branch',
            'branch_name', 'company_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar departamentos"""

    class Meta:
        model = Department
        fields = ['id', 'name', 'description']


class BranchSerializer(serializers.ModelSerializer):
    """Serializer completo para Sucursales"""

    company_name = serializers.CharField(
        source='company.name',
        read_only=True
    )
    manager_name = serializers.CharField(
        source='manager.get_full_name',
        read_only=True,
        allow_null=True
    )
    departments = DepartmentListSerializer(
        many=True,
        read_only=True
    )
    total_departments = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'address', 'phone', 'company',
            'company_name', 'manager', 'manager_name',
            'is_active', 'departments', 'total_departments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_departments(self, obj):
        """Obtener total de departamentos usando la propiedad del modelo"""
        return obj.total_departments

    def validate_manager(self, value):
        """Validar que el manager sea tipo employee"""
        if value and value.user_type != 'employee':
            raise serializers.ValidationError(
                "El gerente debe ser un usuario de tipo 'employee'"
            )
        return value


class BranchListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar sucursales"""

    manager_name = serializers.CharField(
        source='manager.get_full_name',
        read_only=True,
        allow_null=True
    )
    total_departments = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'address', 'phone',
            'manager_name', 'is_active', 'total_departments'
        ]

    def get_total_departments(self, obj):
        """Obtener total de departamentos usando la propiedad del modelo"""
        return obj.total_departments


class CompanySerializer(serializers.ModelSerializer):
    """Serializer completo para Empresas"""

    owner_name = serializers.CharField(
        source='owner.get_full_name',
        read_only=True
    )
    owner_email = serializers.CharField(
        source='owner.email',
        read_only=True
    )
    branches = BranchListSerializer(
        many=True,
        read_only=True
    )
    total_branches = serializers.SerializerMethodField()
    total_departments = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'address', 'phone', 'email',
            'owner', 'owner_name', 'owner_email',
            'branches', 'total_branches', 'total_departments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_total_branches(self, obj):
        """Obtener total de sucursales usando la propiedad del modelo"""
        return obj.total_branches

    def get_total_departments(self, obj):
        """Obtener total de departamentos usando la propiedad del modelo"""
        return obj.total_departments

    def create(self, validated_data):
        """Asignar automáticamente el owner del request"""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar empresas"""

    total_branches = serializers.SerializerMethodField()
    total_departments = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'address',
            'phone', 'email', 'total_branches',
            'total_departments', 'created_at'
        ]

    def get_total_branches(self, obj):
        """Obtener total de sucursales usando la propiedad del modelo"""
        return obj.total_branches

    def get_total_departments(self, obj):
        """Obtener total de departamentos usando la propiedad del modelo"""
        return obj.total_departments
