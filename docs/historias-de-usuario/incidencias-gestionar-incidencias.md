# HU-INCI-001: Registrar y gestionar incidencias de equipos

Como docente, tecnico o administrador de KairOs, quiero reportar una
incidencia de hardware o software sobre un equipo especifico, para
que el area tecnica le de seguimiento hasta resolverla.

## Criterios de aceptacion

1. Puedo reportar una incidencia indicando espacio, equipo, tipo
   (hardware/software) y descripcion.
2. Como docente, despues de reportar una incidencia no veo acciones
   de editar ni eliminar sobre ella.
3. Como administrador o tecnico, puedo cambiar el estado de una
   incidencia (pendiente / en proceso / resuelto), editarla o
   eliminarla.
4. Al marcar una incidencia como resuelta, el sistema registra la
   fecha de resolucion automaticamente.
5. Puedo ver quien registro cada incidencia en el listado/detalle,
   sin importar su rol.
6. Puedo filtrar el listado de incidencias por espacio, equipo, tipo
   y estado.

## Alcance tecnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `GET/POST /api/v1/incidencias/`, `PATCH/DELETE /api/v1/incidencias/{id}/` |
| Service | `backend/incidencias/services/incidencia_service.py` |
| Repository | `backend/incidencias/repositories/incidencia_repository.py` |
| Auditoria | `backend/shared/mixins/audit.py` (AuditableMixin) |

## RF / RNF relacionados

- RF: `docs/requerimientos-funcionales/incidencias-gestionar-incidencias.md`
- RNF: `docs/requerimientos-no-funcionales/incidencias-gestionar-incidencias.md`

## Notas de implementacion

{Pendiente de completar al cerrar el desarrollo.}

## Enlaces

- PR: {URL del pull request}
- Issue GitHub: {URL del issue}
