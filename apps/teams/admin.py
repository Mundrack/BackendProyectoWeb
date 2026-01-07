from django.contrib import admin
from .models import Team, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    fields = ['user', 'role']
    raw_id_fields = ['user']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'department', 'team_type', 'leader',
        'member_count', 'is_active', 'created_at'
    ]
    list_filter = ['team_type', 'is_active', 'created_at', 'department__branch__company']
    search_fields = ['name', 'description', 'leader__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TeamMemberInline]
    raw_id_fields = ['leader']

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'department', 'team_type', 'description')
        }),
        ('Liderazgo', {
            'fields': ('leader', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'team', 'role', 'get_company',
        'get_branch', 'assigned_at'
    ]
    list_filter = ['role', 'assigned_at', 'team__team_type']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'team__name']
    readonly_fields = ['assigned_at']
    raw_id_fields = ['user', 'team']

    def get_company(self, obj):
        return obj.team.department.branch.company.name
    get_company.short_description = 'Empresa'

    def get_branch(self, obj):
        return obj.team.department.branch.name
    get_branch.short_description = 'Sucursal'
