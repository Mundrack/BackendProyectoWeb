from django.contrib import admin
from .models import Comparison, ComparisonAudit, Recommendation


class ComparisonAuditInline(admin.TabularInline):
    model = ComparisonAudit
    extra = 1
    fields = ['audit', 'order']


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'audit_count', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ComparisonAuditInline]

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'audit', 'category', 'priority',
        'is_auto_generated', 'created_at'
    ]
    list_filter = [
        'priority', 'is_auto_generated', 'category', 'created_at'
    ]
    search_fields = ['audit__title', 'category', 'recommendation_text']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Auditoría', {
            'fields': ('audit',)
        }),
        ('Recomendación', {
            'fields': ('category', 'recommendation_text', 'priority')
        }),
        ('Metadata', {
            'fields': ('is_auto_generated', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
