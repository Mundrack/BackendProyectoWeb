# API DOCUMENTATION - Sistema de Auditorías Empresariales

**Base URL:** `http://127.0.0.1:8000`
**Autenticación:** JWT Bearer Token
**Content-Type:** `application/json`

---

## TABLA DE CONTENIDOS

1. [Autenticación](#1-autenticación)
2. [Empresas y Estructura](#2-empresas-y-estructura)
3. [Plantillas](#3-plantillas)
4. [Auditorías](#4-auditorías)
5. [Dashboard](#5-dashboard)
6. [Comparaciones y Recomendaciones](#6-comparaciones-y-recomendaciones)
7. [Equipos y Jerarquía](#7-equipos-y-jerarquía)

---

## 1. AUTENTICACIÓN

### 1.1 Registro de Usuario

**POST** `/api/auth/register/`

**Body:**
```json
{
  "email": "usuario@email.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "user_type": "owner"  // "owner" o "employee"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "email": "usuario@email.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "user_type": "owner"
  },
  "message": "Usuario registrado exitosamente"
}
```

### 1.2 Login

**POST** `/api/auth/login/`

**Body:**
```json
{
  "email": "usuario@email.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "usuario@email.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "user_type": "owner"
  }
}
```

**Guardar el `access` token para usarlo en todas las peticiones:**
```javascript
localStorage.setItem('access_token', response.data.access);
localStorage.setItem('refresh_token', response.data.refresh);
```

### 1.3 Refresh Token

**POST** `/api/auth/refresh/`

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 1.4 Logout

**POST** `/api/auth/logout/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 1.5 Perfil del Usuario

**GET** `/api/auth/me/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "usuario@email.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "user_type": "owner"
}
```

---

## 2. EMPRESAS Y ESTRUCTURA

### 2.1 Listar Empresas

**GET** `/api/companies/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "ACME Corporation",
    "industry": "Tecnología",
    "tax_id": "1234567890001",
    "owner": 1,
    "created_at": "2024-12-30T10:00:00Z"
  }
]
```

### 2.2 Crear Empresa

**POST** `/api/companies/`

**Body:**
```json
{
  "name": "ACME Corporation",
  "industry": "Tecnología",
  "tax_id": "1234567890001"
}
```

**Response (201):** (Igual que el objeto de la lista)

### 2.3 Listar Sucursales

**GET** `/api/branches/`

**Query Params (opcional):**
- `company={id}` - Filtrar por empresa

**Response (200):**
```json
[
  {
    "id": 1,
    "company": 1,
    "company_name": "ACME Corporation",
    "name": "Quito Norte",
    "address": "Av. Naciones Unidas",
    "city": "Quito",
    "country": "Ecuador"
  }
]
```

### 2.4 Crear Sucursal

**POST** `/api/branches/`

**Body:**
```json
{
  "company": 1,
  "name": "Quito Norte",
  "address": "Av. Naciones Unidas",
  "city": "Quito",
  "country": "Ecuador"
}
```

### 2.5 Listar Departamentos

**GET** `/api/departments/`

**Query Params (opcional):**
- `branch={id}` - Filtrar por sucursal

**Response (200):**
```json
[
  {
    "id": 1,
    "branch": 1,
    "branch_name": "Quito Norte",
    "company_name": "ACME Corporation",
    "name": "Tecnología",
    "description": "Departamento de TI"
  }
]
```

### 2.6 Crear Departamento

**POST** `/api/departments/`

**Body:**
```json
{
  "branch": 1,
  "name": "Tecnología",
  "description": "Departamento de TI"
}
```

---

## 3. PLANTILLAS

### 3.1 Listar Plantillas

**GET** `/api/templates/`

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "ISO 27701 - Gestión de la Privacidad",
    "description": "Plantilla ISO 27701...",
    "category": "Privacidad",
    "is_active": true,
    "questions_count": 115,
    "created_at": "2024-12-30T10:00:00Z"
  }
]
```

### 3.2 Ver Detalle de Plantilla

**GET** `/api/templates/{id}/`

**Response (200):**
```json
{
  "id": 1,
  "name": "ISO 27701 - Gestión de la Privacidad",
  "description": "...",
  "category": "Privacidad",
  "is_active": true,
  "questions": [
    {
      "id": 1,
      "question_text": "¿Se ha designado un responsable de privacidad?",
      "category": "Organización de la Privacidad",
      "weight": 1
    }
  ]
}
```

### 3.3 Vista Previa de Plantilla

**GET** `/api/templates/{id}/preview/`

**Response (200):**
```json
{
  "template": {
    "id": 1,
    "name": "ISO 27701"
  },
  "questions_by_category": {
    "Organización de la Privacidad": [
      {
        "id": 1,
        "question_text": "¿Se ha designado un responsable de privacidad?",
        "weight": 1
      }
    ]
  },
  "total_questions": 115
}
```

---

## 4. AUDITORÍAS

### 4.1 Listar Auditorías

**GET** `/api/audits/`

**Query Params (opcional):**
- `company={id}` - Filtrar por empresa
- `status={status}` - Filtrar por estado (draft, in_progress, completed)
- `assigned_to={user_id}` - Filtrar por asignado

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Auditoría ISO 27701 - Q1 2024",
    "company": 1,
    "company_name": "ACME Corporation",
    "template": 1,
    "template_name": "ISO 27701",
    "status": "completed",
    "start_date": "2024-01-15",
    "end_date": "2024-01-30",
    "score_percentage": 86.67,
    "assigned_to": 2,
    "assigned_to_name": "Juan Pérez",
    "created_at": "2024-01-10T10:00:00Z"
  }
]
```

### 4.2 Crear Auditoría

**POST** `/api/audits/`

**Body:**
```json
{
  "title": "Auditoría ISO 27701 - Q1 2024",
  "company": 1,
  "template": 1,
  "start_date": "2024-01-15",
  "end_date": "2024-01-30",
  "assigned_to": 2  // opcional
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "Auditoría ISO 27701 - Q1 2024",
  "company": 1,
  "template": 1,
  "status": "draft",
  "score_percentage": null,
  "created_at": "2024-01-10T10:00:00Z"
}
```

### 4.3 Iniciar Auditoría

**POST** `/api/audits/{id}/start/`

**Response (200):**
```json
{
  "message": "Auditoría iniciada exitosamente",
  "status": "in_progress"
}
```

### 4.4 Enviar Respuesta

**POST** `/api/audits/{id}/submit-response/`

**Body:**
```json
{
  "question": 1,
  "response": "yes",  // "yes", "no", "partial", "na"
  "comments": "Comentarios adicionales"  // opcional
}
```

**Response (201):**
```json
{
  "id": 1,
  "question": 1,
  "response": "yes",
  "comments": "Comentarios adicionales",
  "submitted_at": "2024-01-15T14:30:00Z"
}
```

### 4.5 Completar Auditoría

**POST** `/api/audits/{id}/complete/`

**Response (200):**
```json
{
  "message": "Auditoría completada exitosamente",
  "status": "completed",
  "score_percentage": 86.67
}
```

### 4.6 Reporte de Auditoría

**GET** `/api/audits/{id}/report/`

**Response (200):**
```json
{
  "audit": {
    "id": 1,
    "title": "Auditoría ISO 27701 - Q1 2024",
    "status": "completed",
    "score_percentage": 86.67
  },
  "score_by_category": {
    "Organización de la Privacidad": {
      "score": 450,
      "max_score": 500,
      "percentage": 90.0
    }
  },
  "responses": [
    {
      "question_text": "¿Se ha designado un responsable?",
      "category": "Organización",
      "response": "yes",
      "score": 100
    }
  ],
  "summary": {
    "total_questions": 115,
    "answered": 115,
    "yes": 95,
    "partial": 15,
    "no": 5,
    "na": 0
  }
}
```

### 4.7 Desglose de Puntuación

**GET** `/api/audits/{id}/score-breakdown/`

**Response (200):**
```json
{
  "total_score": 8650,
  "max_score": 10000,
  "percentage": 86.5,
  "categories": {
    "Organización de la Privacidad": {
      "score": 450,
      "max_score": 500,
      "percentage": 90.0,
      "questions_count": 5
    }
  }
}
```

---

## 5. DASHBOARD

### 5.1 Estadísticas Generales

**GET** `/api/dashboard/stats/`

**Query Params (opcional):**
- `company={id}` - Filtrar por empresa
- `start_date=2024-01-01` - Fecha inicio
- `end_date=2024-12-31` - Fecha fin

**Response (200):**
```json
{
  "total_audits": 25,
  "completed_audits": 20,
  "in_progress_audits": 3,
  "draft_audits": 2,
  "average_score": 85.5,
  "total_companies": 5,
  "total_employees": 15
}
```

### 5.2 Auditorías por Estado

**GET** `/api/dashboard/audits-by-status/`

**Response (200):**
```json
[
  {
    "status": "completed",
    "count": 20
  },
  {
    "status": "in_progress",
    "count": 3
  },
  {
    "status": "draft",
    "count": 2
  }
]
```

### 5.3 Auditorías por Mes

**GET** `/api/dashboard/audits-by-month/`

**Query Params (opcional):**
- `year=2024`

**Response (200):**
```json
[
  {
    "month": "2024-01",
    "count": 5,
    "average_score": 85.5
  },
  {
    "month": "2024-02",
    "count": 8,
    "average_score": 87.2
  }
]
```

### 5.4 Top Empresas

**GET** `/api/dashboard/top-companies/`

**Query Params (opcional):**
- `limit=10` - Cantidad de resultados

**Response (200):**
```json
[
  {
    "company_id": 1,
    "company_name": "ACME Corporation",
    "audits_count": 10,
    "average_score": 88.5
  }
]
```

### 5.5 Auditorías Recientes

**GET** `/api/dashboard/recent-audits/`

**Query Params (opcional):**
- `limit=10`

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Auditoría ISO 27701",
    "company_name": "ACME Corporation",
    "status": "completed",
    "score_percentage": 86.67,
    "created_at": "2024-01-10T10:00:00Z"
  }
]
```

### 5.6 Rendimiento por Categoría

**GET** `/api/dashboard/category-performance/`

**Response (200):**
```json
[
  {
    "category": "Organización de la Privacidad",
    "average_score": 88.5,
    "audits_count": 20
  }
]
```

---

## 6. COMPARACIONES Y RECOMENDACIONES

### 6.1 Comparar Auditorías (Rápida)

**POST** `/api/comparisons/compare/`

**Body:**
```json
{
  "audit_ids": [1, 2, 3]  // Mínimo 2, máximo 5
}
```

**Response (200):**
```json
{
  "audits": [
    {
      "id": 1,
      "title": "Auditoría Q1 2024",
      "score_percentage": 86.67,
      "score_by_category": {
        "Organización": 90.0,
        "Seguridad": 85.5
      }
    }
  ],
  "comparative_analysis": {
    "same_template": true,
    "total_audits": 3,
    "highest_score": {
      "audit_id": 3,
      "score": 92.5
    },
    "lowest_score": {
      "audit_id": 1,
      "score": 86.67
    },
    "average_score": 89.39,
    "score_range": 5.83,
    "score_variance": 6.85
  },
  "categories_comparison": {
    "Organización de la Privacidad": {
      "audits": [
        {
          "audit_id": 1,
          "percentage": 90.0
        }
      ],
      "average": 88.5,
      "highest": 92.0,
      "lowest": 85.0
    }
  }
}
```

### 6.2 Análisis de Tendencias

**POST** `/api/comparisons/trends/`

**Body:**
```json
{
  "audit_ids": [1, 2, 3, 4]  // Deben ser de la misma plantilla
}
```

**Response (200):**
```json
{
  "overall_trend": "improving",  // "improving", "declining", "stable"
  "change_percentage": 6.73,
  "scores_timeline": [86.67, 88.50, 90.25, 92.50],
  "categories_trends": {
    "Organización de la Privacidad": {
      "scores": [85.0, 87.5, 89.0, 91.0],
      "trend": "improving",
      "change_percentage": 7.06
    }
  },
  "audits_count": 4
}
```

### 6.3 Crear Comparación Guardada

**POST** `/api/comparisons/`

**Body:**
```json
{
  "name": "Comparación Q1 vs Q4 2024",
  "description": "Evolución anual",
  "audit_ids": [1, 2, 3]
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Comparación Q1 vs Q4 2024",
  "description": "Evolución anual",
  "audit_count": 3,
  "created_at": "2024-12-30T10:00:00Z"
}
```

### 6.4 Listar Comparaciones Guardadas

**GET** `/api/comparisons/`

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Comparación Q1 vs Q4 2024",
    "audit_count": 3,
    "created_by_name": "Juan Pérez",
    "created_at": "2024-12-30T10:00:00Z"
  }
]
```

### 6.5 Analizar Comparación Guardada

**GET** `/api/comparisons/{id}/analyze/`

**Response:** (Igual que `/compare/`)

### 6.6 Generar Recomendaciones

**POST** `/api/audits/{id}/generate-recommendations/`

**Response (200):**
```json
{
  "message": "Recomendaciones generadas exitosamente",
  "summary": {
    "total": 5,
    "high_priority": 1,
    "medium_priority": 2,
    "low_priority": 2,
    "auto_generated": 5,
    "manual": 0
  },
  "recommendations": [
    {
      "id": 1,
      "category": "Seguridad",
      "recommendation_text": "Se requiere atención inmediata...",
      "priority": "high",
      "is_auto_generated": true,
      "created_at": "2024-12-30T10:00:00Z"
    }
  ]
}
```

**Prioridades automáticas:**
- Score < 60% = `high`
- Score 60-75% = `medium`
- Score 75-85% = `low`
- Score > 85% = `low` (felicitación)

### 6.7 Ver Recomendaciones de Auditoría

**GET** `/api/audits/{id}/recommendations/`

**Response (200):**
```json
[
  {
    "id": 1,
    "audit_title": "Auditoría Q1 2024",
    "category": "Seguridad",
    "recommendation_text": "...",
    "priority": "high",
    "is_auto_generated": true,
    "created_at": "2024-12-30T10:00:00Z"
  }
]
```

### 6.8 Crear Recomendación Manual

**POST** `/api/recommendations/`

**Body:**
```json
{
  "audit": 1,
  "category": "Seguridad Física",
  "recommendation_text": "Implementar sistema biométrico...",
  "priority": "high"  // "high", "medium", "low"
}
```

---

## 7. EQUIPOS Y JERARQUÍA

### 7.1 Listar Equipos

**GET** `/api/teams/`

**Query Params (opcional):**
- `company={id}` - Filtrar por empresa
- `branch={id}` - Filtrar por sucursal
- `department={id}` - Filtrar por departamento
- `team_type={type}` - Filtrar por tipo

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Equipo de Auditoría",
    "team_type": "manager_equipo",
    "team_type_display": "Manager de Equipo",
    "leader_name": "Juan Pérez",
    "member_count": 5,
    "department_name": "Tecnología",
    "branch_name": "Quito Norte",
    "company_name": "ACME Corporation",
    "is_active": true
  }
]
```

### 7.2 Crear Equipo

**POST** `/api/teams/`

**Body:**
```json
{
  "name": "Equipo de Auditoría",
  "department": 1,
  "team_type": "manager_equipo",  // "gerente_general", "manager_equipo", "miembro_equipo"
  "leader": 2,  // opcional, debe ser employee
  "description": "Equipo principal de auditorías",
  "is_active": true
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Equipo de Auditoría",
  "department": 1,
  "department_detail": {
    "id": 1,
    "name": "Tecnología",
    "branch_name": "Quito Norte"
  },
  "team_type": "manager_equipo",
  "team_type_display": "Manager de Equipo",
  "leader": 2,
  "leader_detail": {
    "id": 2,
    "name": "Juan Pérez",
    "email": "juan@example.com"
  },
  "description": "Equipo principal de auditorías",
  "is_active": true,
  "members_detail": [],
  "member_count": 0,
  "created_at": "2024-12-30T10:00:00Z"
}
```

### 7.3 Ver Detalle de Equipo

**GET** `/api/teams/{id}/`

**Response (200):** (Igual que crear, pero con miembros)

### 7.4 Agregar Miembro al Equipo

**POST** `/api/teams/{id}/add_member/`

**Body:**
```json
{
  "user_id": 5,  // Debe ser employee
  "role": "member"  // "leader" o "member"
}
```

**Response (200):**
```json
{
  "message": "Miembro agregado exitosamente",
  "member": {
    "id": 10,
    "team": 1,
    "user": 5,
    "user_name": "María García",
    "user_email": "maria@example.com",
    "role": "member",
    "role_display": "Miembro",
    "assigned_at": "2024-12-30T10:30:00Z"
  }
}
```

### 7.5 Remover Miembro del Equipo

**POST** `/api/teams/{id}/remove_member/`

**Body:**
```json
{
  "user_id": 5
}
```

**Response (200):**
```json
{
  "message": "Miembro removido exitosamente"
}
```

### 7.6 Cambiar Rol de Miembro

**POST** `/api/teams/{id}/change_member_role/`

**Body:**
```json
{
  "user_id": 5,
  "new_role": "leader"  // "leader" o "member"
}
```

**Response (200):**
```json
{
  "message": "Rol actualizado exitosamente",
  "member": {
    "id": 10,
    "user": 5,
    "role": "leader",
    "role_display": "Líder"
  }
}
```

**Nota:** Si cambias a leader, el líder anterior baja automáticamente a member.

### 7.7 Estadísticas de Equipo

**GET** `/api/teams/{id}/stats/`

**Response (200):**
```json
{
  "team_id": 1,
  "team_name": "Equipo de Auditoría",
  "team_type": "manager_equipo",
  "members_count": 5,
  "leaders_count": 1,
  "audits": {
    "total": 15,
    "completed": 10,
    "in_progress": 5
  },
  "is_active": true
}
```

### 7.8 Jerarquía Organizacional Completa

**GET** `/api/teams/hierarchy/?company_id={id}`

**Response (200):**
```json
{
  "company_id": 1,
  "company_name": "ACME Corporation",
  "branches": [
    {
      "branch_id": 1,
      "branch_name": "Quito Norte",
      "departments": [
        {
          "department_id": 1,
          "department_name": "Tecnología",
          "teams": [
            {
              "team_id": 1,
              "team_name": "Equipo de Auditoría",
              "team_type": "manager_equipo",
              "team_type_display": "Manager de Equipo",
              "leader": {
                "id": 2,
                "name": "Juan Pérez",
                "email": "juan@example.com"
              },
              "members": [
                {
                  "id": 2,
                  "name": "Juan Pérez",
                  "email": "juan@example.com",
                  "role": "leader",
                  "role_display": "Líder",
                  "assigned_at": "2024-12-30T10:00:00Z"
                },
                {
                  "id": 5,
                  "name": "María García",
                  "email": "maria@example.com",
                  "role": "member",
                  "role_display": "Miembro",
                  "assigned_at": "2024-12-30T10:30:00Z"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### 7.9 Equipos de un Empleado

**GET** `/api/employees/{user_id}/teams/`

**Response (200):**
```json
{
  "user_id": 5,
  "teams_count": 2,
  "teams": [
    {
      "membership_id": 10,
      "team_id": 1,
      "team_name": "Equipo de Auditoría",
      "team_type": "manager_equipo",
      "role": "member",
      "department": "Tecnología",
      "branch": "Quito Norte",
      "company": "ACME Corporation",
      "assigned_at": "2024-12-30T10:30:00Z"
    }
  ]
}
```

---

## CÓDIGOS DE RESPUESTA HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Petición exitosa |
| 201 | Created - Recurso creado exitosamente |
| 204 | No Content - Eliminado exitosamente |
| 400 | Bad Request - Error en los datos enviados |
| 401 | Unauthorized - Token inválido o expirado |
| 403 | Forbidden - Sin permisos para esta acción |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

---

## MANEJO DE ERRORES

### Error de Validación (400)

```json
{
  "field_name": [
    "Este campo es requerido"
  ]
}
```

### Error de Autenticación (401)

```json
{
  "detail": "Token inválido o expirado"
}
```

### Error de Permisos (403)

```json
{
  "detail": "No tienes permiso para realizar esta acción"
}
```

### Error No Encontrado (404)

```json
{
  "detail": "No encontrado"
}
```

---

## EJEMPLOS DE INTEGRACIÓN CON AXIOS

### Configuración Base

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor para agregar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('http://127.0.0.1:8000/api/auth/refresh/', {
          refresh: refreshToken
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Logout
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### Ejemplo: Login

```javascript
const login = async (email, password) => {
  try {
    const response = await api.post('/api/auth/login/', {
      email,
      password
    });

    const { access, refresh, user } = response.data;

    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(user));

    return { success: true, user };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data || 'Error al iniciar sesión'
    };
  }
};
```

### Ejemplo: Listar Auditorías

```javascript
const getAudits = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`/api/audits/?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error al obtener auditorías:', error);
    throw error;
  }
};

// Uso
const audits = await getAudits({ company: 1, status: 'completed' });
```

### Ejemplo: Crear Auditoría

```javascript
const createAudit = async (auditData) => {
  try {
    const response = await api.post('/api/audits/', auditData);
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      errors: error.response?.data
    };
  }
};

// Uso
const result = await createAudit({
  title: 'Auditoría Q1 2024',
  company: 1,
  template: 1,
  start_date: '2024-01-15',
  end_date: '2024-01-30'
});
```

### Ejemplo: Dashboard Stats

```javascript
const getDashboardStats = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`/api/dashboard/stats/?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error al obtener estadísticas:', error);
    throw error;
  }
};

// Uso
const stats = await getDashboardStats({ company: 1 });
```

### Ejemplo: Comparar Auditorías

```javascript
const compareAudits = async (auditIds) => {
  try {
    const response = await api.post('/api/comparisons/compare/', {
      audit_ids: auditIds
    });
    return response.data;
  } catch (error) {
    console.error('Error al comparar auditorías:', error);
    throw error;
  }
};

// Uso
const comparison = await compareAudits([1, 2, 3]);
```

### Ejemplo: Jerarquía de Equipos

```javascript
const getOrganizationHierarchy = async (companyId) => {
  try {
    const response = await api.get(`/api/teams/hierarchy/?company_id=${companyId}`);
    return response.data;
  } catch (error) {
    console.error('Error al obtener jerarquía:', error);
    throw error;
  }
};

// Uso
const hierarchy = await getOrganizationHierarchy(1);
```

---

## FLUJO TÍPICO DE USO

### 1. Autenticación y Setup Inicial

```javascript
// 1. Login
await login('owner@empresa.com', 'password');

// 2. Crear empresa
const company = await api.post('/api/companies/', {
  name: 'Mi Empresa',
  industry: 'Tecnología',
  tax_id: '1234567890'
});

// 3. Crear sucursal
const branch = await api.post('/api/branches/', {
  company: company.data.id,
  name: 'Oficina Principal',
  city: 'Quito',
  country: 'Ecuador'
});

// 4. Crear departamento
const department = await api.post('/api/departments/', {
  branch: branch.data.id,
  name: 'Tecnología'
});
```

### 2. Crear y Completar Auditoría

```javascript
// 1. Crear auditoría
const audit = await api.post('/api/audits/', {
  title: 'Auditoría ISO 27701',
  company: company.data.id,
  template: 1, // ISO 27701
  start_date: '2024-01-15',
  end_date: '2024-01-30'
});

// 2. Iniciar auditoría
await api.post(`/api/audits/${audit.data.id}/start/`);

// 3. Enviar respuestas
await api.post(`/api/audits/${audit.data.id}/submit-response/`, {
  question: 1,
  response: 'yes',
  comments: 'Todo en orden'
});

// 4. Completar auditoría
await api.post(`/api/audits/${audit.data.id}/complete/`);

// 5. Ver reporte
const report = await api.get(`/api/audits/${audit.data.id}/report/`);
```

### 3. Dashboard y Comparaciones

```javascript
// 1. Obtener estadísticas
const stats = await api.get('/api/dashboard/stats/');

// 2. Comparar auditorías
const comparison = await api.post('/api/comparisons/compare/', {
  audit_ids: [1, 2, 3]
});

// 3. Generar recomendaciones
const recommendations = await api.post('/api/audits/1/generate-recommendations/');
```

### 4. Gestión de Equipos

```javascript
// 1. Crear equipo
const team = await api.post('/api/teams/', {
  name: 'Equipo de Auditoría',
  department: department.data.id,
  team_type: 'manager_equipo'
});

// 2. Agregar miembros
await api.post(`/api/teams/${team.data.id}/add_member/`, {
  user_id: 5,
  role: 'member'
});

// 3. Ver jerarquía
const hierarchy = await api.get(`/api/teams/hierarchy/?company_id=${company.data.id}`);
```

---

## VALIDACIONES IMPORTANTES

### Auditorías

- ✅ Solo se pueden comparar auditorías completadas (`status='completed'`)
- ✅ Las comparaciones de tendencias requieren auditorías de la misma plantilla
- ✅ Mínimo 2 auditorías, máximo 5 para comparaciones
- ✅ Las respuestas válidas son: `yes`, `no`, `partial`, `na`

### Equipos

- ✅ Solo usuarios con `user_type='employee'` pueden ser miembros de equipos
- ✅ Un usuario no puede estar duplicado en el mismo equipo
- ✅ Solo puede haber un líder por equipo
- ✅ Al cambiar líder, el anterior baja automáticamente a member

### Permisos

- ✅ **Owners** pueden gestionar empresas, auditorías y equipos
- ✅ **Employees** pueden ver y responder auditorías asignadas
- ✅ Solo el owner de la empresa puede modificar sus recursos

---

## NOTAS FINALES

- Todos los timestamps están en formato ISO 8601 UTC
- Las fechas se envían en formato `YYYY-MM-DD`
- Los IDs son enteros positivos
- Los porcentajes están en escala 0-100
- Las respuestas de listas están paginadas (20 items por página)

---

**Fecha de Documentación:** 30 de Diciembre de 2024
**Versión API:** 1.0.0
**Base URL:** http://127.0.0.1:8000
