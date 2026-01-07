from django.db import models
from django.conf import settings
from apps.audits.models import Audit


class Comparison(models.Model):
    """
    Comparación entre múltiples auditorías.
    Permite guardar y reutilizar comparaciones.
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Comparación'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    audits = models.ManyToManyField(
        Audit,
        through='ComparisonAudit',
        related_name='comparisons',
        verbose_name='Auditorías'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comparisons',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comparisons'
        verbose_name = 'Comparación'
        verbose_name_plural = 'Comparaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.audit_count} auditorías)"

    @property
    def audit_count(self):
        """Cantidad de auditorías en la comparación"""
        return self.audits.count()


class ComparisonAudit(models.Model):
    """
    Tabla intermedia para la relación Many-to-Many.
    Permite metadata adicional si es necesario.
    """

    comparison = models.ForeignKey(
        Comparison,
        on_delete=models.CASCADE,
        verbose_name='Comparación'
    )
    audit = models.ForeignKey(
        Audit,
        on_delete=models.CASCADE,
        verbose_name='Auditoría'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de la auditoría en la comparación'
    )

    class Meta:
        db_table = 'comparison_audits'
        unique_together = ['comparison', 'audit']
        ordering = ['order']

    def __str__(self):
        return f"{self.comparison.name} - {self.audit.title}"


class Recommendation(models.Model):
    """
    Recomendaciones generadas para una auditoría.
    Pueden ser automáticas o manuales.
    """

    PRIORITY_CHOICES = [
        ('high', 'Alta'),
        ('medium', 'Media'),
        ('low', 'Baja'),
    ]

    audit = models.ForeignKey(
        Audit,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name='Auditoría'
    )
    category = models.CharField(
        max_length=200,
        verbose_name='Categoría'
    )
    recommendation_text = models.TextField(
        verbose_name='Texto de Recomendación'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        verbose_name='Prioridad'
    )
    is_auto_generated = models.BooleanField(
        default=False,
        verbose_name='Generada Automáticamente',
        help_text='True si fue generada por el sistema'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_recommendations',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendations'
        verbose_name = 'Recomendación'
        verbose_name_plural = 'Recomendaciones'
        ordering = ['audit', '-priority', 'category']
        indexes = [
            models.Index(fields=['audit']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_auto_generated']),
        ]

    def __str__(self):
        return f"{self.audit.title} - {self.category} ({self.get_priority_display()})"
