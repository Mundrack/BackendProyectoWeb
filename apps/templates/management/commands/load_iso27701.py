from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.templates.models import AuditTemplate, TemplateQuestion
import json
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Carga la plantilla ISO 27701 en la base de datos'

    def handle(self, *args, **kwargs):
        # Buscar o crear un usuario owner para asignar la plantilla
        owner = User.objects.filter(user_type='owner').first()

        if not owner:
            self.stdout.write(
                self.style.ERROR('No existe ningún usuario owner. Crea uno primero.')
            )
            return

        # Cargar el JSON
        fixture_path = os.path.join(
            os.path.dirname(__file__),
            '../../fixtures/iso27701_template.json'
        )

        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Verificar si ya existe
        existing = AuditTemplate.objects.filter(
            iso_standard='27701',
            name=data['name']
        ).first()

        if existing:
            self.stdout.write(
                self.style.WARNING(
                    f'La plantilla "{data["name"]}" ya existe. No se creará duplicada.'
                )
            )
            return

        # Crear la plantilla
        template = AuditTemplate.objects.create(
            name=data['name'],
            iso_standard=data['iso_standard'],
            description=data['description'],
            is_active=data['is_active'],
            version=data['version'],
            created_by=owner
        )

        # Crear las preguntas
        questions = [
            TemplateQuestion(
                template=template,
                category=q['category'],
                question_text=q['question_text'],
                order_num=q['order_num'],
                max_score=q['max_score'],
                is_required=q['is_required'],
                help_text=q['help_text']
            )
            for q in data['questions']
        ]

        TemplateQuestion.objects.bulk_create(questions)

        self.stdout.write(
            self.style.SUCCESS(
                f'Plantilla "{template.name}" creada exitosamente con {len(questions)} preguntas'
            )
        )
