# Requerimientos y Arquitectura del Backend — KairOs

Sistema de Gestión Integral de Laboratorios, Infraestructura Tecnológica, Equipamiento y Mantenimiento.

---

## 1. Visión General del Backend

El backend de **KairOs** está construido sobre **Python 3.12** y **Django 5.2 / 6.0** utilizando **Django REST Framework (DRF)**. Proporciona una API RESTful desacoplada, segura y de alto rendimiento que alimenta la aplicación frontend desarrollada en Vue 3.

### 1.1 Objetivos Arquitecturales
- **Separación de Responsabilidades (SRP):** Cada capa del sistema (vistas, servicios de dominio, repositorios, serializadores y modelos) tiene un único propósito bien delimitado.
- **Seguridad Robusta:** Autenticación por JSON Web Tokens (JWT) con rotación de tokens, soporte para Google Identity Services (OAuth 2.0 / OpenID Connect) y control de acceso basado en roles (RBAC).
- **Trazabilidad Inmutable:** Registro de auditoría global de todas las mutaciones relevantes en el sistema (`historial`).
- **Integridad y Resiliencia:** Borrado lógico (*Soft Delete*) en modelos operativos, manejo centralizado de excepciones y transaccionalidad atómica en operaciones críticas.

---

## 2. Stack Tecnológico

| Componente | Tecnología | Versión / Detalle |
|------------|------------|-------------------|
| **Lenguaje** | Python | 3.12.x |
| **Framework Base** | Django | 5.2+ / 6.0+ |
| **API Framework** | Django REST Framework | 3.16.x |
| **Autenticación JWT** | SimpleJWT | 5.3.x (`rest_framework_simplejwt`) |
| **Federación de Identidad** | Google Auth Library | `google-auth` |
| **Base de Datos Principal** | PostgreSQL | 15+ (producción / desarrollo local) |
| **Base de Datos Pruebas** | SQLite3 | En memoria / archivo para suite de tests |
| **Gestión de CORS** | django-cors-headers | 4.3.x |
| **Filtrado Avanzado** | django-filter | 25.x |
| **Testing** | Django Test / Pytest | Test runner integrado de Django |

---

## 3. Estructura de Aplicaciones y Módulos

El proyecto organiza el backend en aplicaciones modulares dentro del directorio `backend/`:

```
backend/
├── server/                 # Configuración central (settings, urls, wsgi, asgi)
├── shared/                 # Modelos base, viewsets base, excepciones y utilitarios comunes
├── autenticacion/          # Login local, Google OAuth, refresco y recuperación de claves
├── usuarios/               # Gestión de usuarios, perfiles técnicos y roles
├── espacios/               # Edificios, pabellones, laboratorios, asignaciones y planos
├── equipos/                # Inventario de hardware, especificaciones y componentes internos
├── software/               # Catálogo de productos de software y licencias instaladas
├── mantenimiento/          # Tickets preventivos y correctivos, asignación de técnicos
├── incidencias/            # Reportes de fallas en equipos e infraestructura
└── historial/              # Log de auditoría global e inmutable del sistema
```

---

## 4. Patrón Arquitectónico en Capas (Service-Layer Pattern)

Para evitar controladores sobrecargados (*Fat Views*) o modelos hinchados (*Fat Models*), el backend sigue estrictamente el patrón de capas:

```
[ Cliente HTTP (Frontend) ]
             │
             ▼
[ 1. View / ViewSet ] ─── Valida petición y delega a servicios
             │
             ▼
[ 2. Service Layer ] ──── Contiene la lógica de negocio y transacciones
        │          │
        ▼          ▼
[ Serializer ]  [ Repositorio / Modelo ORM ]
                         │
                         ▼
             [ Base de Datos PostgreSQL ]
```

### 4.1 Capas del Backend
1. **Modelos (`models.py`):** Define el esquema relacional. Heredan de `shared.models.BaseModel` para contar automáticamente con:
   - `created_at` (fecha de creación automática).
   - `updated_at` (fecha de última modificación).
   - `created_by` (usuario autor).
   - `updated_by` (usuario editor).
   - `is_deleted` (bandera para borrado lógico).
2. **Serializadores (`serializers/`):** Validan formatos de entrada (payloads JSON) y transforman instancias de modelos a representaciones JSON limpias para la respuesta.
3. **Servicios (`services/`):** Implementan las reglas de negocio puras, validaciones complejas, cálculo de métricas y disparadores del log de auditoría.
4. **Vistas / ViewSets (`views/`):** Controladores delgados que heredan de `shared.base.BaseViewSet` o `APIView`. Gestionan la petición HTTP, autorizan permisos y devuelven respuestas estandarizadas.

---

## 5. Requerimientos de Seguridad y Autenticación

### 5.1 Mecanismos de Autenticación
- **JWT (JSON Web Tokens):**
  - **Access Token:** Tiempo de vida de 1 hora (`ACCESS_TOKEN_LIFETIME = 1 hour`).
  - **Refresh Token:** Tiempo de vida de 7 días (`REFRESH_TOKEN_LIFETIME = 7 days`) con rotación automática (`ROTATE_REFRESH_TOKENS = True`).
  - Cabecera requerida: `Authorization: Bearer <access_token>`.
- **Google OAuth 2.0 (SSO):**
  - Recepción de ID Token del frontend generado por Google Identity Services.
  - Validación externa de firma, vigencia y audiencia (`GOOGLE_CLIENT_ID`) mediante `GoogleAuthService`.
  - Auto-registro seguro para usuarios del dominio institucional autorizado.

### 5.2 Control de Acceso Basado en Roles (RBAC)
Los usuarios del sistema cuentan con uno de los siguientes 4 roles:
- `admin` (Administrador): Acceso total a todos los módulos, gestión de usuarios, auditoría y configuraciones.
- `tecnico` (Técnico de Soporte): Gestión operativa de espacios, equipos, componentes, órdenes de mantenimiento e incidencias.
- `docente` (Docente): Consulta de software asignado, reporte de incidencias en laboratorios y visualización de recursos.
- `usuario` (Usuario base): Acceso restringido para consulta y autoservicio.

### 5.3 Manejo Centralizado de Excepciones
El backend implementa `shared.exceptions.custom_exception_handler` en `settings.py`:
- Estandariza las respuestas de error en formato `{"error": "<mensaje descriptivo>"}` o `{"detail": "..."}`.
- Convierte excepciones no controladas en HTTP 500 con log sin exponer trazas internas sensibles en producción.

---

## 6. Variables de Entorno Requeridas

El archivo `.env` en la raíz del backend debe incluir:

```env
# Clave secreta de Django
SECRET_KEY=django-insecure-kairos-production-key-change-in-prod

# Modo de depuración (True para desarrollo, False para producción)
DEBUG=True

# Hosts autorizados separados por coma
ALLOWED_HOSTS=localhost,127.0.0.1

# Conexión a Base de Datos PostgreSQL
DB_NAME=kairos_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Client ID de Google para autenticación federada
GOOGLE_CLIENT_ID=tu_google_client_id.apps.googleusercontent.com

# Clave de firma para SimpleJWT (opcional, por defecto usa SECRET_KEY)
SIMPLE_JWT_SECRET_KEY=kairos-jwt-signing-secret
```

---

## 7. Comandos de Gestión y Semillas de Datos

Django incluye comandos personalizados dentro de `backend/`:
- `python manage.py crear_admin_prueba`: Crea o actualiza un usuario administrador local listo para operar (`admin@kairos.test` / `Admin123!`).
- `python manage.py seed_datos_prueba`: Puebla la base de datos con espacios, equipos, perfiles técnicos y órdenes de mantenimiento para entornos de prueba.
- `python manage.py test`: Ejecuta la suite de más de 100 pruebas unitarias e integrales del backend.
