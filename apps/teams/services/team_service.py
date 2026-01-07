from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from apps.teams.models import Team, TeamMember


class TeamService:
    """
    Servicio para manejar la lógica de negocio de equipos.
    """

    @staticmethod
    def add_member_to_team(team_id, user_id, role='member'):
        """
        Agrega un miembro a un equipo.

        Args:
        - team_id: ID del equipo
        - user_id: ID del usuario (debe ser employee)
        - role: 'leader' o 'member'

        Retorna: TeamMember creado
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            team = Team.objects.get(id=team_id)
            user = User.objects.get(id=user_id)

            # Validar que el usuario sea employee
            if user.user_type != 'employee':
                raise ValidationError(
                    "Solo usuarios de tipo 'employee' pueden ser miembros de equipos"
                )

            # Validar que no exista ya
            if TeamMember.objects.filter(team=team, user=user).exists():
                raise ValidationError(
                    f"{user.get_full_name()} ya es miembro de {team.name}"
                )

            # Si es líder, actualizar el team.leader
            if role == 'leader':
                team.leader = user
                team.save()

            # Crear el TeamMember
            member = TeamMember.objects.create(
                team=team,
                user=user,
                role=role
            )

            return member

        except (Team.DoesNotExist, User.DoesNotExist):
            raise ValidationError("Equipo o usuario no encontrado")

    @staticmethod
    def remove_member_from_team(team_id, user_id):
        """
        Remueve un miembro de un equipo.

        Args:
        - team_id: ID del equipo
        - user_id: ID del usuario
        """
        try:
            team = Team.objects.get(id=team_id)
            member = TeamMember.objects.get(team=team, user_id=user_id)

            # Si es el líder, limpiar team.leader
            if member.role == 'leader':
                team.leader = None
                team.save()

            member.delete()

        except (Team.DoesNotExist, TeamMember.DoesNotExist):
            raise ValidationError("Equipo o miembro no encontrado")

    @staticmethod
    def change_member_role(team_id, user_id, new_role):
        """
        Cambia el rol de un miembro en un equipo.

        Args:
        - team_id: ID del equipo
        - user_id: ID del usuario
        - new_role: 'leader' o 'member'
        """
        try:
            team = Team.objects.get(id=team_id)
            member = TeamMember.objects.get(team=team, user_id=user_id)

            # Si cambia a líder, actualizar team.leader
            if new_role == 'leader':
                # Si ya hay un líder, cambiar su rol a member
                if team.leader and team.leader.id != user_id:
                    old_leader_member = TeamMember.objects.filter(
                        team=team,
                        user=team.leader
                    ).first()
                    if old_leader_member:
                        old_leader_member.role = 'member'
                        old_leader_member.save()

                team.leader_id = user_id
                team.save()

            # Si cambia de líder a member, limpiar team.leader
            elif member.role == 'leader' and new_role == 'member':
                team.leader = None
                team.save()

            member.role = new_role
            member.save()

            return member

        except (Team.DoesNotExist, TeamMember.DoesNotExist):
            raise ValidationError("Equipo o miembro no encontrado")

    @staticmethod
    def get_hierarchy(company_id):
        """
        Obtiene la jerarquía completa de una empresa.

        Retorna estructura organizada por:
        - Empresa
          - Sucursales
            - Departamentos
              - Equipos (ordenados por team_type)
                - Miembros
        """
        from apps.companies.models import Company

        try:
            company = Company.objects.prefetch_related(
                'branches__departments__teams__members__user'
            ).get(id=company_id)

            hierarchy = {
                'company_id': company.id,
                'company_name': company.name,
                'branches': []
            }

            for branch in company.branches.all():
                branch_data = {
                    'branch_id': branch.id,
                    'branch_name': branch.name,
                    'departments': []
                }

                for department in branch.departments.all():
                    dept_data = {
                        'department_id': department.id,
                        'department_name': department.name,
                        'teams': []
                    }

                    for team in department.teams.all():
                        team_data = {
                            'team_id': team.id,
                            'team_name': team.name,
                            'team_type': team.team_type,
                            'team_type_display': team.get_team_type_display(),
                            'leader': {
                                'id': team.leader.id,
                                'name': team.leader.get_full_name(),
                                'email': team.leader.email
                            } if team.leader else None,
                            'members': []
                        }

                        for member in team.members.all():
                            team_data['members'].append({
                                'id': member.user.id,
                                'name': member.user.get_full_name(),
                                'email': member.user.email,
                                'role': member.role,
                                'role_display': member.get_role_display(),
                                'assigned_at': member.assigned_at.isoformat()
                            })

                        dept_data['teams'].append(team_data)

                    branch_data['departments'].append(dept_data)

                hierarchy['branches'].append(branch_data)

            return hierarchy

        except Company.DoesNotExist:
            raise ValidationError("Empresa no encontrada")

    @staticmethod
    def get_employee_teams(user_id):
        """
        Obtiene todos los equipos de un empleado.
        """
        memberships = TeamMember.objects.filter(
            user_id=user_id
        ).select_related(
            'team__department__branch__company'
        )

        return [
            {
                'membership_id': m.id,
                'team_id': m.team.id,
                'team_name': m.team.name,
                'team_type': m.team.team_type,
                'role': m.role,
                'department': m.team.department.name,
                'branch': m.team.department.branch.name,
                'company': m.team.department.branch.company.name,
                'assigned_at': m.assigned_at.isoformat()
            }
            for m in memberships
        ]

    @staticmethod
    def get_team_stats(team_id):
        """
        Obtiene estadísticas de un equipo.
        """
        try:
            team = Team.objects.get(id=team_id)

            members_count = team.members.count()
            leaders_count = team.members.filter(role='leader').count()

            # Contar auditorías asignadas a miembros del equipo
            from apps.audits.models import Audit
            member_ids = team.members.values_list('user_id', flat=True)

            audits_stats = {
                'total': Audit.objects.filter(assigned_to_id__in=member_ids).count(),
                'completed': Audit.objects.filter(
                    assigned_to_id__in=member_ids,
                    status='completed'
                ).count(),
                'in_progress': Audit.objects.filter(
                    assigned_to_id__in=member_ids,
                    status='in_progress'
                ).count()
            }

            return {
                'team_id': team.id,
                'team_name': team.name,
                'team_type': team.team_type,
                'members_count': members_count,
                'leaders_count': leaders_count,
                'audits': audits_stats,
                'is_active': team.is_active
            }

        except Team.DoesNotExist:
            raise ValidationError("Equipo no encontrado")
