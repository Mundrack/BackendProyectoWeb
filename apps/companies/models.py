from django.db import models
from django.conf import settings


class Company(models.Model):
    """Empresa/Organización principal"""

    name = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Empresa'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_companies',
        verbose_name='Propietario',
        limit_choices_to={'user_type': 'owner'}
    )
    address = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Dirección'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Email Corporativo'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['name']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    @property
    def total_branches(self):
        """Cantidad total de sucursales"""
        return self.branches.count()

    @property
    def total_departments(self):
        """Cantidad total de departamentos en todas las sucursales"""
        return Department.objects.filter(branch__company=self).count()


class Branch(models.Model):
    """Sucursal de una empresa"""

    name = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Sucursal'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='branches',
        verbose_name='Empresa'
    )
    address = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Dirección'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_branches',
        verbose_name='Gerente de Sucursal'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'branches'
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        ordering = ['company', 'name']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['manager']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"

    @property
    def total_departments(self):
        """Cantidad de departamentos en esta sucursal"""
        return self.departments.count()


class Department(models.Model):
    """Departamento dentro de una sucursal"""

    name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Departamento'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name='Sucursal'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['branch', 'name']
        indexes = [
            models.Index(fields=['branch']),
        ]

    def __str__(self):
        return f"{self.branch.name} - {self.name}"
