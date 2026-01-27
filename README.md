# Sistema de Auditorías Empresariales - Backend API

## Información del Proyecto

**Framework:** Django + Django REST Framework
**Base de Datos:** PostgreSQL (Supabase)
**Autenticación:** JWT
**Versión:** 1.0.0

---

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Iniciar servidor
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000`

---

## Documentación para Frontend

Toda la documentación de la API está en:

**[API_DOCUMENTATION_FRONTEND.md](API_DOCUMENTATION_FRONTEND.md)**

Este documento contiene:
- Todos los endpoints disponibles
- Ejemplos de peticiones y respuestas
- Códigos de integración con Axios
- Manejo de autenticación y errores
- Flujos completos de uso

---

## Estructura del Proyecto

```
backend/
├── apps/
│   ├── authentication/    # FASE 1: Autenticación JWT
│   ├── companies/        # FASE 2: Empresas y Sucursales
│   ├── templates/        # FASE 3: Plantillas de Auditoría
│   ├── audits/          # FASE 4: Auditorías (CORE)
│   ├── dashboard/       # FASE 5: Dashboard y Estadísticas
│   ├── comparisons/     # FASE 6: Comparaciones y Recomendaciones
│   └── teams/           # FASE 7: Equipos y Jerarquía
├── audit_system/
│   └── settings/
│       ├── base.py
│       └── development.py
└── manage.py
```

---

## Módulos Implementados

### ✅ FASE 1: Autenticación
- Login/Logout con JWT
- Registro de usuarios (Owner/Employee)
- Refresh tokens

### ✅ FASE 2: Empresas y Estructura
- Empresas
- Sucursales
- Departamentos

### ✅ FASE 3: Plantillas
- Plantillas de auditoría
- Preguntas categorizadas
- ISO 27701 precargada

### ✅ FASE 4: Auditorías (CORE)
- Crear y gestionar auditorías
- Sistema de scoring automático
- Workflow: draft → in_progress → completed
- Reportes detallados

### ✅ FASE 5: Dashboard
- Estadísticas generales
- Gráficos y métricas
- Tendencias temporales

### ✅ FASE 6: Comparaciones
- Comparar 2-5 auditorías
- Análisis de tendencias
- Recomendaciones automáticas

### ✅ FASE 7: Equipos
- Gestión de equipos
- Asignación de empleados
- Jerarquía organizacional

---

## Documentación Técnica Completa

Para una visión detallada de la arquitectura, modelo de datos y flujos del sistema, consulta el archivo maestro de documentación en la raíz del proyecto:

📄 **[DOCUMENTACION_TECNICA.md](../DOCUMENTACION_TECNICA.md)**

---

## Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (admin)
python manage.py createsuperuser

# Verificar proyecto
python manage.py check

# Ejecutar tests
python manage.py test

# Shell de Django
python manage.py shell
```

---

## Admin de Django

Acceso: `http://127.0.0.1:8000/admin/`

Todas las apps están configuradas en el admin con:
- Filtros
- Búsqueda
- Relaciones inline
- Estadísticas

---

## Base de Datos

**Proveedor:** Supabase (PostgreSQL)

**Configuración:** Ver `audit_system/settings/development.py`

**Tablas:**
- users (autenticación)
- companies, branches, departments
- audit_templates, template_questions
- audits, audit_responses
- comparisons, comparison_audits, recommendations
- teams, team_members

---

## Soporte

Para dudas sobre la API, consultar: **API_DOCUMENTATION_FRONTEND.md**
