# RF-INCI-001: Registrar y gestionar incidencias de equipos

## Descripción

El sistema debe permitir reportar incidencias (fallas o problemas) de
hardware o software sobre un equipo especifico dentro de un espacio, y
darles seguimiento hasta su resolucion mediante un estado.

## Criterios funcionales

- Administradores, tecnicos y docentes pueden reportar (crear) una
  incidencia.
- Solo administradores y tecnicos pueden cambiar el estado, editar o
  eliminar una incidencia. Un docente no puede modificar ni eliminar
  una incidencia despues de reportarla.
- Toda incidencia esta asociada obligatoriamente a un espacio y a un
  equipo (no se contemplan incidencias generales sin equipo en este
  modulo).
- El tipo de incidencia admite: Hardware y Software.
- Los campos requeridos son espacio, equipo, tipo y descripcion.
- El estado admite: Pendiente, En Proceso y Resuelto. Por defecto una
  incidencia nueva queda en Pendiente.
- Al cambiar el estado a Resuelto, el sistema registra
  automaticamente la fecha de resolucion. Si el estado vuelve a
  Pendiente o En Proceso, la fecha de resolucion se limpia.
- La persona que registro la incidencia (`created_by`, heredado de
  auditoria estandar) es visible en el panel de administracion,
  independientemente de su rol.
- El listado admite filtros por espacio, equipo, tipo y estado.
- La eliminacion es un borrado logico (`is_deleted=True`).

## Reglas de negocio

- `fecha_resolucion` solo tiene valor cuando `estado='resuelto'`; se
  limpia automaticamente ante cualquier otro estado.
- El campo `equipo` no puede cambiarse a nulo (es obligatorio en todo
  momento).

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET /api/v1/incidencias/` |
| API | `POST /api/v1/incidencias/` |
| API | `PATCH /api/v1/incidencias/{id}/` |
| API | `DELETE /api/v1/incidencias/{id}/` |
| API | `GET /api/v1/incidencias/estadisticas/` |
| Backend | `backend/incidencias/repositories/incidencia_repository.py` |
| Backend | `backend/incidencias/services/incidencia_service.py` |
| Backend | `backend/incidencias/serializers/incidencia_serializers.py` |
| Backend | `backend/incidencias/views/incidencia_views.py` |

## Notas

Las incidencias generales del espacio sin equipo asociado (tipo
lista de tareas pendientes de la oficina) quedan fuera de alcance de
este modulo; se evaluaran en un modulo aparte.
