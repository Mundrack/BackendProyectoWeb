from django.contrib import admin
from .models import Audit, AuditResponse


class AuditResponseInline(admin.TabularInline):
    model = AuditResponse
    extra = 0
    fields = ['question', 'score', 'notes', 'evidence_file']
    readonly_fields = ['responded_at']
    can_delete = False


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company', 'branch', 'status',
        'score_percentage', 'assigned_to', 'scheduled_date',
        'created_at'
    ]
    list_filter = ['status', 'scheduled_date', 'created_at', 'company']
    search_fields = ['title', 'company__name', 'assigned_to__email']
    readonly_fields = [
        'total_score', 'max_possible_score', 'score_percentage',
        'started_at', 'completed_at', 'created_at', 'updated_at'
    ]
    inlines = [AuditResponseInline]

    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'template', 'status')
        }),
        ('Asignación', {
            'fields': ('company', 'branch', 'assigned_to', 'created_by', 'scheduled_date')
        }),
        ('Scores', {
            'fields': ('total_score', 'max_possible_score', 'score_percentage'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
    )


@admin.register(AuditResponse)
class AuditResponseAdmin(admin.ModelAdmin):
    list_display = [
        'audit', 'question_preview', 'score',
        'has_evidence', 'responded_at'
    ]
    list_filter = ['audit__status', 'responded_at']
    search_fields = ['audit__title', 'question__question_text', 'notes']
    readonly_fields = ['responded_at']

    def question_preview(self, obj):
        return f"Q{obj.question.order_num}: {obj.question.question_text[:50]}..."
    question_preview.short_description = 'Pregunta'

    def has_evidence(self, obj):
        return bool(obj.evidence_file)
    has_evidence.boolean = True
    has_evidence.short_description = 'Evidencia'
