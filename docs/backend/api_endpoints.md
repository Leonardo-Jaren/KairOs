# Catálogo Completo de Endpoints de la API — KairOs Backend

Base URL en entorno local: `http://localhost:8000/api/v1`

---

## 1. Módulo de Autenticación (`/api/v1/auth/`)

| Método | Endpoint | Roles Permitidos | Descripción | Payload / Parámetros | Respuesta Exitosa |
|--------|----------|------------------|-------------|----------------------|-------------------|
| `POST` | `/auth/login/` | Anónimo | Inicio de sesión tradicional por correo y contraseña. | `{"correo": "...", "password": "..."}` | `{"access": "...", "refresh": "...", "usuario": {...}}` (200 OK) |
| `POST` | `/auth/google/` | Anónimo | Inicio de sesión federado mediante Google Identity Services (SSO). | `{"token": "<google_id_token>"}` | `{"access": "...", "refresh": "...", "usuario": {...}}` (200 OK) |
| `POST` | `/auth/refresh/` | Anónimo | Renovación silenciosa de Access Token usando Refresh Token. | `{"refresh": "<refresh_token>"}` | `{"access": "<nuevo_access_token>"}` (200 OK) |
| `POST` | `/auth/password-reset/` | Anónimo | Solicitud de restablecimiento de contraseña vía correo. | `{"correo": "..."}` | `{"detail": "Correo de restablecimiento enviado."}` (200 OK) |
| `POST` | `/auth/password-reset-confirm/` | Anónimo | Confirmación de restablecimiento con token temporal. | `{"uid": "...", "token": "...", "new_password": "..."}` | `{"detail": "Contraseña restablecida con éxito."}` (200 OK) |

---

## 2. Módulo de Usuarios (`/api/v1/usuarios/`)

| Método | Endpoint | Roles Permitidos | Descripción | Payload / Parámetros |
|--------|----------|------------------|-------------|----------------------|
| `GET` | `/usuarios/` | `admin`, `tecnico` | Listado paginado de usuarios con filtros (`search`, `rol`, `activo`). | Query: `?page=1&search=pedro&rol=tecnico` |
| `POST` | `/usuarios/` | `admin` | Creación de nuevo usuario con rol y contraseña inicial. | `{"nombre": "...", "apellido": "...", "correo": "...", "dni": "...", "rol": "tecnico", "password": "..."}` |
| `GET` | `/usuarios/{id}/` | `admin`, `tecnico` | Detalle completo de un usuario por su identificador. | - |
| `PUT` / `PATCH` | `/usuarios/{id}/` | `admin` | Actualización parcial o total de datos del usuario. | Campos editables |
| `DELETE` | `/usuarios/{id}/` | `admin` | Borrado lógico del usuario (`is_active = False` / `is_deleted = True`). | - |
| `GET` | `/usuarios/estadisticas/` | `admin`, `tecnico` | Métricas consolidadas de usuarios totales, activos y por rol. | - |

---

## 3. Módulo de Espacios y Edificios (`/api/v1/espacios/`)

| Método | Endpoint | Roles Permitidos | Descripción | Payload / Parámetros |
|--------|----------|------------------|-------------|----------------------|
| `GET` | `/espacios/` | `admin`, `tecnico` | Listado de laboratorios, aulas y salas de cómputo. | Query: `?search=lab&tipo=laboratorio&pabellon=Pabellon 1` |
| `POST` | `/espacios/` | `admin` | Registro de un nuevo espacio físico. | `{"codigo_espacio": "LAB-204", "tipo": "laboratorio", "pabellon": "...", "piso": "2"}` |
| `GET` | `/espacios/{id}/` | `admin`, `tecnico` | Detalle de un espacio incluyendo su `configuracion_plano` y equipos. | - |
| `PATCH` | `/espacios/{id}/disposicion/` | `admin`, `tecnico` | Actualiza la matriz y coordenadas de puestos del plano interactivo. | `{"filas": 5, "columnas": 6, "posiciones": [...]}` |
| `GET` | `/espacios/edificios/` | `admin`, `tecnico` | Listado de edificios/pabellones del campus tecnológico. | Query: `?activo=true` |
| `PATCH` | `/espacios/edificios/{id}/croquis-piso/` | `admin` | Actualiza el mapa vectorial o configuración de croquis por piso. | `{"piso": "1", "croquis": {...}}` |
| `GET` | `/espacios/usuarios/` | `admin`, `tecnico` | Asignaciones de usuarios y docentes a laboratorios. | Query: `?espacio_id=17` |
| `POST` | `/espacios/usuarios/` | `admin` | Asigna un usuario a un espacio con un rol operativo específico. | `{"espacio": 17, "usuario": 5, "tipo_responsabilidad": "responsable"}` |
| `DELETE` | `/espacios/usuarios/{id}/` | `admin` | Elimina la asignación de un usuario a un espacio. | - |

---

## 4. Módulo de Equipos y Componentes (`/api/v1/equipos/`)

| Método | Endpoint | Roles Permitidos | Descripción | Payload / Parámetros |
|--------|----------|------------------|-------------|----------------------|
| `GET` | `/equipos/` | `admin`, `tecnico` | Listado de equipos de cómputo con filtros por estado, tipo y espacio. | Query: `?estado=en_uso&tipo_equipo=desktop&espacio=17` |
| `POST` | `/equipos/` | `admin`, `tecnico` | Registro de nuevo equipo informático. | `{"codigo": "LAB205-PC01", "numero_serie": "SN-...", "marca": "Dell", "modelo": "OptiPlex", "tipo_equipo": "desktop", "espacio": 17, ...}` |
| `GET` | `/equipos/{id}/` | `admin`, `tecnico` | Ficha técnica detallada del equipo, red, componentes e historial. | - |
| `PUT` / `PATCH` | `/equipos/{id}/` | `admin`, `tecnico` | Modificación de datos del equipo (ej. cambio de estado o reubicación). | Campos a actualizar |
| `DELETE` | `/equipos/{id}/` | `admin` | Baja lógica del equipo del inventario institucional. | - |
| `GET` | `/equipos/opciones/` | `admin`, `tecnico` | Enums de tipos de equipo, estados y modos de adquisición para formularios. | - |
| `GET` | `/equipos/componentes/` | `admin`, `tecnico` | Inventario de componentes internos (CPU, RAM, SSD, GPU, etc.). | Query: `?equipo_id=10&tipo=ram` |
| `POST` | `/equipos/componentes/` | `admin`, `tecnico` | Registro o adición de componente de hardware a un equipo. | `{"equipo": 10, "tipo": "ram", "capacidad": "16GB", "marca": "Kingston", ...}` |

---

## 5. Módulo de Software y Licenciamiento (`/api/v1/software/`)

| Método | Endpoint | Roles Permitidos | Descripción | Payload / Parámetros |
|--------|----------|------------------|-------------|----------------------|
| `GET` | `/software/productos/` | `admin`, `tecnico`, `docente` | Catálogo de productos de software, conteo de licencias y costos. | Query: `?search=matlab&tipo_licencia=volumen` |
| `POST` | `/software/productos/` | `admin`, `tecnico` | Registro de nuevo software en el catálogo. | `{"software": "MATLAB", "version": "R2024a", "tipo_licencia": "volumen", "licencias_totales": 50, ...}` |
| `GET` | `/software/productos/opciones/` | `admin`, `tecnico` | Enums de tipos de licencia y opciones de filtrado. | - |
| `GET` | `/software/instalaciones/` | `admin`, `tecnico`, `docente` | Mapeo de software instalado por equipo informático. | Query: `?equipo=15&producto_software=3` |
| `POST` | `/software/instalaciones/` | `admin`, `tecnico` | Asocia una instalación de software a un equipo específico. | `{"equipo": 15, "producto_software": 3, "numero_licencia_usado": "..."}` |
| `DELETE` | `/software/instalaciones/{id}/` | `admin`, `tecnico` | Desinstalación o desvinculación de licencia de un equipo. | - |

---

## 6. Módulo de Mantenimiento (`/api/v1/mantenimiento/`)

| Método | Endpoint | Roles Permitidos | Descripción | Payload / Parámetros |
|--------|----------|------------------|-------------|----------------------|
| `GET` | `/mantenimiento/` | `admin`, `tecnico` | Listado de órdenes de mantenimiento preventivo y correctivo. | Query: `?estado=pendiente&tipo_mantenimiento=correctivo` |
| `POST` | `/mantenimiento/` | `admin`, `tecnico` | Creación de una orden de mantenimiento con asignación técnica. | `{"equipo": 12, "tipo_mantenimiento": "correctivo", "descripcion": "...", "tecnicos_ids": [1, 2]}` |
| `GET` | `/mantenimiento/{id}/` | `admin`, `tecnico` | Detalle del ticket de mantenimiento, acciones ejecutadas y técnicos. | - |
| `PATCH` | `/mantenimiento/{id}/` | `admin`, `tecnico` | Actualización de estado del ticket (`en_proceso`, `resuelto`, `cancelado`). | `{"estado": "resuelto"}` |
| `GET` | `/mantenimiento/tecnicos-disponibles/` | `admin`, `tecnico` | Lista de personal técnico activo para asignación en tickets. | - |

---

## 7. Módulo de Incidencias (`/api/v1/incidencias/`)

| Método | Endpoint | Roles Permitidos | Descripción | Payload / Parámetros |
|--------|----------|------------------|-------------|----------------------|
| `GET` | `/incidencias/` | `admin`, `tecnico`, `docente` | Listado de fallas reportadas por docentes o soporte. | Query: `?estado=pendiente&tipo_incidencia=hardware` |
| `POST` | `/incidencias/` | `admin`, `tecnico`, `docente` | Reporte de nueva falla sobre un equipo o laboratorio. | `{"espacio": 17, "equipo": 22, "tipo_incidencia": "hardware", "descripcion": "..."}` |
| `PATCH` | `/incidencias/{id}/` | `admin`, `tecnico` | Actualización de estado o resolución de la incidencia. | `{"estado": "resuelto", "fecha_resolucion": "2026-09-14"}` |
| `GET` | `/incidencias/espacios-opciones/` | Todos | Opciones de espacios para selector de reportes. | - |
| `GET` | `/incidencias/equipos-opciones/` | Todos | Opciones de equipos filtrados por espacio. | Query: `?espacio_id=17` |

---

## 8. Módulo de Historial y Auditoría (`/api/v1/historial/`)

| Método | Endpoint | Roles Permitidos | Descripción | Payload / Parámetros |
|--------|----------|------------------|-------------|----------------------|
| `GET` | `/historial/` | `admin`, `tecnico` | Consulta del log inmutable de auditoría del sistema con filtros cronológicos y por módulo. | Query: `?tipo_evento=equipo.cambio_estado&fecha_inicio=2026-09-01` |
| `GET` | `/historial/{id}/` | `admin`, `tecnico` | Detalle del evento de auditoría con JSON de datos extra (estado anterior y nuevo). | - |
| `POST`/`PUT`/`DELETE` | `/historial/` | *Ninguno* | **Bloqueado:** Los eventos de auditoría se generan exclusivamente desde los servicios internos y nunca mediante peticiones HTTP directas. | HTTP 405 Method Not Allowed |
