# RF-HIST-001: Registro y Consulta de Historial de Auditoría

| Campo | Valor |
|-------|-------|
| Modulo | Historial y Auditoría |
| Version | 1.0 |
| Fecha | 2026-09-14 |
| Autor | Equipo KairOs |
| Estado | Aprobado |

## Descripcion

El sistema debe registrar de forma automática, inmutable y centralizada todos los eventos críticos de creación, modificación, asignación y baja que ocurran en cualquier módulo (equipos, mantenimiento, espacios, usuarios, etc.). Dicho log debe estar disponible para consulta por parte de los administradores y personal técnico con capacidades de filtrado por rango de fechas, módulo y usuario responsable.

## Actores

- Administrador
- Técnico

## Precondiciones

- El usuario debe tener rol `admin` o `tecnico`.
- Los eventos son emitidos automáticamente por la capa de servicios (`services/`) al efectuar mutaciones exitosas.

## Flujo principal

1. El usuario accede a la vista de auditoría (`/historial`).
2. El frontend solicita el listado cronológico de eventos al endpoint `/api/v1/historial/`.
3. El usuario visualiza la tabla con los últimos eventos registrados:
   - Marca de tiempo del evento.
   - Tipo de evento (ej: `equipo.creado`, `mantenimiento.resuelto`, `espacio.modificado`).
   - Usuario actor responsable de la acción.
   - Descripción legible en español.
4. El usuario puede aplicar filtros por fecha inicial, fecha final o tipo de evento.
5. El usuario puede seleccionar un evento para inspeccionar el detalle técnico en `datos_extra` (valores anteriores vs. nuevos).

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Intento de mutación directa vía HTTP (`POST`, `PUT`, `DELETE` en `/api/v1/historial/`) | Retorna HTTP 405 Method Not Allowed. La auditoría es inmutable desde la API. |
| Consulta sin filtros | Retorna los eventos ordenados descendentemente por fecha con paginación estándar. |
| Usuario con rol `docente` o `usuario` intenta acceder a `/historial` | El guard de navegación de frontend y el permission class de backend bloquean la petición retornando HTTP 403 Forbidden. |

## Reglas de negocio

- Los eventos de auditoría son de solo lectura a través de la API.
- Ningún usuario, ni siquiera el administrador, puede alterar o suprimir registros de la tabla `historial`.
- Las entradas registran el objeto afectado mediante `django.contrib.contenttypes` (`content_type` y `object_id`).

## Criterios de aceptacion

- [x] Registra eventos de auditoría al mutar entidades críticas.
- [x] Provee interfaz gráfica de consulta con filtrado por fecha y tipo de evento.
- [x] Bloquea métodos de escritura (`POST`, `PUT`, `DELETE`) en la API de historial.
- [x] Restringe el acceso exclusivamente a roles `admin` y `tecnico`.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET /api/v1/historial/` |
| API Detalle | `GET /api/v1/historial/{id}/` |
| Backend Modelo | `backend/historial/models.py` |
| Backend ViewSet | `backend/historial/views/historial_views.py` |
| Frontend Vista | `frontend/src/views/historial/HistorialView.vue` |

## Notas

Proporciona trazabilidad completa para cumplimiento de normas de control patrimonial y seguridad de la información.
