from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Team, TeamMember
from apps.companies.serializers import DepartmentSerializer

User = get_user_model()


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer para Miembros de Equipo"""

    user_name = serializers.CharField(
        source='user.get_full_name',
        read_only=True
    )
    user_email = serializers.CharField(
        source='user.email',
        read_only=True
    )
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True
    )

    class Meta:
        model = TeamMember
        fields = [
            'id', 'team', 'user', 'user_name',
            'user_email', 'role', 'role_display',
            'assigned_at'
        ]
        read_only_fields = ['id', 'assigned_at']

    def validate_user(self, value):
        """Validar que el usuario sea tipo employee"""
        if value.user_type != 'employee':
            raise serializers.ValidationError(
                "Solo usuarios de tipo 'employee' pueden ser miembros de equipos"
            )
        return value


class TeamMemberListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar miembros"""

    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'user_name', 'user_email', 'role', 'role_display']


class TeamSerializer(serializers.ModelSerializer):
    """Serializer completo para Equipos"""

    department_detail = DepartmentSerializer(source='department', read_only=True)
    leader_detail = serializers.SerializerMethodField()
    members_detail = TeamMemberListSerializer(source='members', many=True, read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    team_type_display = serializers.CharField(source='get_team_type_display', read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'department', 'department_detail',
            'team_type', 'team_type_display', 'leader', 'leader_detail',
            'description', 'is_active', 'members_detail', 'member_count',
            'company_name', 'branch_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_leader_detail(self, obj):
        if obj.leader:
            return {
                'id': obj.leader.id,
                'name': obj.leader.get_full_name(),
                'email': obj.leader.email
            }
        return None

    def validate_leader(self, value):
        """Validar que el líder sea tipo employee"""
        if value and value.user_type != 'employee':
            raise serializers.ValidationError(
                "El líder debe ser un usuario de tipo 'employee'"
            )
        return value


class TeamListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar equipos"""

    leader_name = serializers.CharField(
        source='leader.get_full_name',
        read_only=True,
        allow_null=True
    )
    member_count = serializers.IntegerField(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    team_type_display = serializers.CharField(source='get_team_type_display', read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'team_type', 'team_type_display',
            'leader_name', 'member_count', 'department_name',
            'branch_name', 'company_name', 'is_active'
        ]


class AddMemberSerializer(serializers.Serializer):
    """Serializer para agregar miembros a un equipo"""

    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(
        choices=['leader', 'member'],
        default='member'
    )

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            if user.user_type != 'employee':
                raise serializers.ValidationError(
                    "Solo usuarios de tipo 'employee' pueden ser miembros"
                )
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")


class ChangeMemberRoleSerializer(serializers.Serializer):
    """Serializer para cambiar rol de miembro"""

    user_id = serializers.IntegerField()
    new_role = serializers.ChoiceField(choices=['leader', 'member'])
