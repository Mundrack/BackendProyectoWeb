from django.contrib import admin
from .models import AuditTemplate, TemplateQuestion


class TemplateQuestionInline(admin.TabularInline):
    model = TemplateQuestion
    extra = 1
    fields = ['order_num', 'category', 'question_text', 'max_score', 'is_required']
    ordering = ['order_num']


@admin.register(AuditTemplate)
class AuditTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'iso_standard', 'version', 'is_active',
        'total_questions', 'max_possible_score', 'created_by', 'created_at'
    ]
    list_filter = ['is_active', 'iso_standard', 'created_at', 'created_by']
    search_fields = ['name', 'iso_standard', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TemplateQuestionInline]

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'iso_standard', 'description', 'version')
        }),
        ('Configuración', {
            'fields': ('created_by', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TemplateQuestion)
class TemplateQuestionAdmin(admin.ModelAdmin):
    list_display = [
        'order_num', 'template', 'category',
        'question_preview', 'max_score', 'is_required'
    ]
    list_filter = ['template', 'category', 'is_required', 'max_score']
    search_fields = ['question_text', 'category', 'template__name']
    readonly_fields = ['created_at']
    ordering = ['template', 'order_num']

    def question_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_preview.short_description = 'Pregunta'

    fieldsets = (
        ('Plantilla', {
            'fields': ('template', 'order_num')
        }),
        ('Pregunta', {
            'fields': ('category', 'question_text', 'help_text')
        }),
        ('Configuración', {
            'fields': ('max_score', 'is_required')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
