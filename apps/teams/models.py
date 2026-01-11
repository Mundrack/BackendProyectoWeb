from django.db import models
from django.conf import settings
from apps.companies.models import Department


class Team(models.Model):
    """
    Equipo de trabajo dentro de un departamento.
    Los equipos tienen una jerarquía definida por team_type.
    """

    TEAM_TYPE_CHOICES = [
        ('gerente_general', 'Gerente General'),
        ('manager_equipo', 'Manager de Equipo'),
        ('miembro_equipo', 'Miembro de Equipo'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Equipo'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='teams',
        verbose_name='Departamento'
    )
    team_type = models.CharField(
        max_length=50,
        choices=TEAM_TYPE_CHOICES,
        verbose_name='Tipo de Equipo',
        help_text='Define el nivel jerárquico del equipo'
    )
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams',
        verbose_name='Líder del Equipo',
        limit_choices_to={'user_type': 'employee'}
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['department', 'team_type', 'name']
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['team_type']),
            models.Index(fields=['leader']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.department.branch.name} - {self.name} ({self.get_team_type_display()})"

    @property
    def company(self):
        """Empresa a la que pertenece el equipo"""
        return self.department.branch.company

    @property
    def branch(self):
        """Sucursal a la que pertenece el equipo"""
        return self.department.branch


class TeamMember(models.Model):
    """
    Relación entre usuarios (employees) y equipos.
    Un empleado puede estar en múltiples equipos.
    """

    ROLE_CHOICES = [
        ('leader', 'Líder'),
        ('member', 'Miembro'),
    ]

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Equipo'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_memberships',
        verbose_name='Usuario',
        limit_choices_to={'user_type': 'employee'}
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Rol en el Equipo'
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Asignación'
    )

    class Meta:
        db_table = 'team_members'
        verbose_name = 'Miembro de Equipo'
        verbose_name_plural = 'Miembros de Equipo'
        unique_together = ['team', 'user']
        ordering = ['team', 'role', 'user']
        indexes = [
            models.Index(fields=['team']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name} ({self.get_role_display()})"

    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError

        # Validar que el usuario sea tipo employee
        if self.user.user_type != 'employee':
            raise ValidationError({
                'user': 'Solo usuarios de tipo "employee" pueden ser miembros de equipos'
            })

        # Si es líder, debe coincidir con el líder del equipo
        if self.role == 'leader' and self.team.leader != self.user:
            raise ValidationError({
                'role': 'El usuario debe ser el líder designado del equipo'
            })
