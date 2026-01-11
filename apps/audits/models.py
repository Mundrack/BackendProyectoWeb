from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.companies.models import Company, Branch
from apps.templates.models import AuditTemplate, TemplateQuestion


class Audit(models.Model):
    """
    Modelo principal de auditoría - CORE del sistema.
    Representa una instancia de auditoría basada en una plantilla.
    """

    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]

    # Información básica
    title = models.CharField(
        max_length=300,
        verbose_name='Título de la Auditoría'
    )
    template = models.ForeignKey(
        AuditTemplate,
        on_delete=models.RESTRICT,
        related_name='audits',
        verbose_name='Plantilla'
    )

    # Asignación
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='audits',
        verbose_name='Empresa'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audits',
        verbose_name='Sucursal'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name='assigned_audits',
        verbose_name='Asignado a (Auditor)',
        help_text='Usuario que ejecutará la auditoría'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_audits',
        verbose_name='Creado por'
    )

    # Estado y fechas
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Programada'
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Iniciado en'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Completado en'
    )

    # Scores
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='Puntaje Total Obtenido'
    )
    max_possible_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='Puntaje Máximo Posible'
    )
    score_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='Porcentaje de Cumplimiento'
    )

    # Notas generales
    notes = models.TextField(
        blank=True,
        verbose_name='Notas Generales'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'audits'
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['company']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.title} - {self.company.name}"

    @property
    def progress_percentage(self):
        """Calcula el porcentaje de preguntas respondidas"""
        total_questions = self.template.total_questions
        answered_questions = self.responses.count()

        if total_questions == 0:
            return 0

        return round((answered_questions / total_questions) * 100, 2)

    @property
    def answered_questions_count(self):
        """Cantidad de preguntas respondidas"""
        return self.responses.count()

    @property
    def total_questions_count(self):
        """Cantidad total de preguntas en la plantilla"""
        return self.template.total_questions

    @property
    def is_complete(self):
        """Verifica si todas las preguntas obligatorias están respondidas"""
        required_questions = self.template.questions.filter(is_required=True).count()
        answered_required = self.responses.filter(
            question__is_required=True
        ).count()

        return required_questions == answered_required

    def calculate_score(self):
        """
        Calcula el score total de la auditoría.
        Retorna dict con total_score, max_possible_score y percentage.
        """
        responses = self.responses.select_related('question').all()

        total = sum(
            response.score
            for response in responses
            if response.score is not None
        )

        max_possible = self.template.max_possible_score

        self.total_score = total
        self.max_possible_score = max_possible

        if max_possible > 0:
            self.score_percentage = round((total / max_possible) * 100, 2)
        else:
            self.score_percentage = 0

        self.save()

        return {
            'total_score': float(self.total_score),
            'max_possible_score': float(self.max_possible_score),
            'percentage': float(self.score_percentage)
        }


class AuditResponse(models.Model):
    """
    Respuesta a una pregunta específica de una auditoría.
    Incluye score, notas y evidencias.
    """

    RESPONSE_TYPE_CHOICES = [
        ('yes', 'Sí'),
        ('no', 'No'),
        ('partial', 'Parcial'),
        ('na', 'No Aplica'),
    ]

    audit = models.ForeignKey(
        Audit,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Auditoría'
    )
    question = models.ForeignKey(
        TemplateQuestion,
        on_delete=models.RESTRICT,
        related_name='responses',
        verbose_name='Pregunta'
    )
    
    # Tipo de respuesta (yes/no/partial/na)
    response_type = models.CharField(
        max_length=10,
        choices=RESPONSE_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Tipo de Respuesta'
    )
    
    score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name='Puntaje',
        help_text='Puntaje otorgado (0 al máximo definido en la pregunta)'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notas/Observaciones'
    )
    evidence_file = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Archivo de Evidencia (URL)',
        help_text='URL del archivo de evidencia en storage'
    )

    responded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Respondido en'
    )

    class Meta:
        db_table = 'audit_responses'
        verbose_name = 'Respuesta de Auditoría'
        verbose_name_plural = 'Respuestas de Auditoría'
        unique_together = ['audit', 'question']
        ordering = ['audit', 'question__order_num']
        indexes = [
            models.Index(fields=['audit']),
            models.Index(fields=['question']),
        ]

    def __str__(self):
        return f"Respuesta Q{self.question.order_num} - {self.audit.title}"

    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError

        # Validar que el score no exceda el máximo de la pregunta
        if self.score is not None and self.score > self.question.max_score:
            raise ValidationError({
                'score': f'El puntaje no puede exceder {self.question.max_score}'
            })

        # Validar que la pregunta pertenezca a la plantilla de la auditoría
        if self.question.template != self.audit.template:
            raise ValidationError({
                'question': 'La pregunta no pertenece a la plantilla de esta auditoría'
            })
