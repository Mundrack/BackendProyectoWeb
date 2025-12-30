from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class AuditTemplate(models.Model):
    """
    Plantilla de auditoría basada en estándares ISO.
    Define el conjunto de preguntas que se usarán en las auditorías.
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Plantilla'
    )
    iso_standard = models.CharField(
        max_length=50,
        verbose_name='Estándar ISO',
        help_text='Ejemplo: 27701, 9001, 27001'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_templates',
        verbose_name='Creado por'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
        help_text='Solo plantillas activas pueden usarse en auditorías'
    )
    version = models.IntegerField(
        default=1,
        verbose_name='Versión',
        validators=[MinValueValidator(1)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'audit_templates'
        verbose_name = 'Plantilla de Auditoría'
        verbose_name_plural = 'Plantillas de Auditoría'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['iso_standard']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.name} ({self.iso_standard}) - v{self.version}"

    @property
    def total_questions(self):
        """Cantidad total de preguntas en la plantilla"""
        return self.questions.count()

    @property
    def max_possible_score(self):
        """Puntaje máximo posible de la plantilla"""
        from django.db.models import Sum
        result = self.questions.aggregate(Sum('max_score'))
        return result['max_score__sum'] or 0

    @property
    def categories(self):
        """Lista de categorías únicas en la plantilla"""
        return self.questions.values_list('category', flat=True).distinct()


class TemplateQuestion(models.Model):
    """
    Pregunta dentro de una plantilla de auditoría.
    Cada pregunta pertenece a una categoría y tiene un orden.
    """

    template = models.ForeignKey(
        AuditTemplate,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Plantilla'
    )
    category = models.CharField(
        max_length=200,
        verbose_name='Categoría',
        help_text='Ejemplo: Política de Privacidad, Gestión de Datos'
    )
    question_text = models.TextField(
        verbose_name='Pregunta'
    )
    order_num = models.IntegerField(
        verbose_name='Orden',
        validators=[MinValueValidator(1)],
        help_text='Orden de la pregunta dentro de la plantilla'
    )
    max_score = models.IntegerField(
        default=5,
        verbose_name='Puntaje Máximo',
        validators=[MinValueValidator(1)],
        help_text='Puntaje máximo que se puede obtener en esta pregunta'
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name='Obligatoria',
        help_text='Si es obligatoria, debe responderse para completar la auditoría'
    )
    help_text = models.TextField(
        blank=True,
        verbose_name='Texto de Ayuda',
        help_text='Información adicional para guiar la respuesta'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'template_questions'
        verbose_name = 'Pregunta de Plantilla'
        verbose_name_plural = 'Preguntas de Plantilla'
        ordering = ['template', 'order_num']
        unique_together = ['template', 'order_num']
        indexes = [
            models.Index(fields=['template', 'order_num']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"Q{self.order_num}: {self.question_text[:50]}..."
