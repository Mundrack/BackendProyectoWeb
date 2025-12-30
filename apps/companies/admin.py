from django.contrib import admin
from .models import Company, Branch, Department


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'total_branches', 'phone', 'created_at']
    list_filter = ['created_at', 'owner']
    search_fields = ['name', 'owner__email', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'owner')
        }),
        ('Contacto', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'manager', 'is_active', 'total_departments', 'created_at']
    list_filter = ['is_active', 'created_at', 'company']
    search_fields = ['name', 'company__name', 'address', 'phone']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'company', 'manager', 'is_active')
        }),
        ('Contacto', {
            'fields': ('address', 'phone')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'get_company', 'created_at']
    list_filter = ['created_at', 'branch__company']
    search_fields = ['name', 'branch__name', 'branch__company__name']
    readonly_fields = ['created_at', 'updated_at']

    def get_company(self, obj):
        return obj.branch.company.name
    get_company.short_description = 'Empresa'

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'branch', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
