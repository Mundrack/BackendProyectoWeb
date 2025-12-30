# Sistema de Auditorías Empresariales - Backend

Sistema de gestión de auditorías ISO para empresas con estructura jerárquica. Proyecto universitario para el curso ISWZ3101-2679 de UDLA.

## Stack Tecnológico

- Django 5.0+
- Django REST Framework
- Simple JWT (autenticación)
- PostgreSQL (Supabase)
- python-decouple

## Características Principales

- Sistema de autenticación JWT
- Modelo de usuario personalizado con roles (owner/employee)
- Integración con Supabase PostgreSQL
- API RESTful completa
- Validaciones de seguridad
- Panel de administración Django

## Estructura del Proyecto

```
backend/
├── audit_system/              # Proyecto principal
│   ├── settings/              # Configuraciones divididas
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   └── authentication/        # App de autenticación
│       ├── models.py          # User model
│       ├── serializers.py     # Serializers
│       ├── views.py           # Views
│       ├── urls.py            # URLs
│       ├── permissions.py     # Permisos custom
│       └── admin.py           # Django Admin
├── core/                      # Utilidades compartidas
├── manage.py
├── requirements.txt
└── .env
```

## Instalación

### 1. Clonar el repositorio

```bash
cd backend
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

El archivo `.env` ya está configurado con las credenciales de Supabase.

### 5. Crear migraciones y migrar

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

Ejemplo:
- Email: admin@test.com
- Password: admin123
- First name: Admin
- Last name: Sistema
- User type: owner

### 7. Ejecutar servidor

```bash
python manage.py runserver
```

El servidor estará disponible en `http://localhost:8000`

## Endpoints API

### Autenticación

#### POST /api/auth/register/
Registrar nuevo usuario

**Request:**
```json
{
  "email": "usuario@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "user_type": "owner"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "full_name": "Nombre Apellido",
    "user_type": "owner",
    "is_active": true,
    "date_joined": "2024-12-29T10:30:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
  }
}
```

#### POST /api/auth/login/
Login de usuario

**Request:**
```json
{
  "email": "usuario@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "full_name": "Nombre Apellido",
    "user_type": "owner",
    "is_active": true,
    "date_joined": "2024-12-29T10:30:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
  }
}
```

#### POST /api/auth/token/refresh/
Refrescar token de acceso

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

#### GET /api/auth/profile/
Obtener perfil del usuario autenticado

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbG...
```

**Response (200):**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "full_name": "Nombre Apellido",
  "user_type": "owner",
  "is_active": true,
  "date_joined": "2024-12-29T10:30:00Z"
}
```

#### PUT /api/auth/profile/
Actualizar perfil del usuario

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbG...
```

**Request:**
```json
{
  "first_name": "Nombre Actualizado",
  "last_name": "Apellido Actualizado"
}
```

#### POST /api/auth/change-password/
Cambiar contraseña del usuario

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbG...
```

**Request:**
```json
{
  "old_password": "SecurePass123",
  "new_password": "NewSecurePass456",
  "new_password_confirm": "NewSecurePass456"
}
```

**Response (200):**
```json
{
  "message": "Contraseña actualizada exitosamente"
}
```

## Permisos Personalizados

### IsOwner
Solo usuarios con `user_type='owner'` tienen acceso.

### IsEmployee
Solo usuarios con `user_type='employee'` tienen acceso.

### IsOwnerOrReadOnly
Los owners pueden realizar cualquier operación, los employees solo lectura.

## Validaciones

- Email único
- Contraseña mínimo 8 caracteres
- user_type solo acepta 'owner' o 'employee'
- Validación de contraseñas comunes
- Validación de contraseñas similares a datos del usuario

## Base de Datos

El proyecto está configurado para usar PostgreSQL en Supabase:

- Host: aws-0-us-east-1.pooler.supabase.com
- Puerto: 6543
- Database: postgres
- Conexión SSL requerida

## Admin Panel

Accede al panel de administración en `http://localhost:8000/admin/`

Características:
- Gestión completa de usuarios
- Filtrado por tipo de usuario
- Búsqueda por email, nombre y apellido
- Ordenamiento por fecha de registro

## Desarrollo

### Crear nueva app

```bash
python manage.py startapp nombre_app
```

Luego agregar la app en `INSTALLED_APPS` en [settings/base.py](audit_system/settings/base.py:13)

### Crear migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Crear superusuario

```bash
python manage.py createsuperuser
```

### Ejecutar tests

```bash
python manage.py test
```

## Configuración de Ambientes

### Desarrollo
Usa `settings/development.py` (por defecto)
- DEBUG = True
- Base de datos Supabase PostgreSQL
- Logging detallado

### Producción
Usa `settings/production.py`
- DEBUG = False
- Configuraciones de seguridad adicionales
- SSL redirect habilitado

Para cambiar el ambiente:
```bash
# Windows
set DJANGO_ENV=production

# Linux/Mac
export DJANGO_ENV=production
```

## Seguridad

- Autenticación JWT con tokens de corta duración
- Blacklist de tokens al hacer logout
- Validación de contraseñas robustas
- CORS configurado para frontend React
- SSL requerido en base de datos
- Headers de seguridad configurados

## Próximas Fases

- FASE 2: Empresas y Sucursales
- FASE 3: Roles y Permisos
- FASE 4: Auditorías
- FASE 5: Dashboard y Reportes

## Autor

Proyecto desarrollado para ISWZ3101-2679 - UDLA

## Licencia

Proyecto académico - Todos los derechos reservados
