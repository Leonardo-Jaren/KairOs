# HU-EQUI-002: Gestionar componentes de hardware de un equipo

Como administrador de KairOs, quiero registrar y mantener actualizados los
componentes de hardware de cada equipo (CPU, RAM, almacenamiento, etc.) para
contar con un inventario detallado a nivel de piezas y ver su historial de
cambios en la línea de tiempo del equipo.

## Criterios de aceptación

1. Puedo ver todos los componentes del sistema en `/componentes`, con filtros
   rápidos por tipo y búsqueda de texto.
2. Puedo ver los componentes de un equipo específico en la pestaña
   "Componentes" del modal de detalle, accesible desde el botón de ojo en
   la tabla de equipos.
3. Puedo agregar un componente indicando equipo, tipo y modelo (descripción
   opcional).
4. Puedo editar el tipo, modelo y descripción de un componente existente, pero
   no cambiarle el equipo.
5. Puedo eliminar un componente con confirmación; la eliminación es lógica.
6. Cada operación (alta, edición, baja) genera un evento de auditoría visible
   en la pestaña "Línea de Tiempo" del equipo afectado.
7. La pestaña "Línea de Tiempo" del detalle de equipo muestra todos los eventos
   de auditoría del equipo (cambios de estado, responsable, espacio y
   componentes) con carga bajo demanda.
8. Los iconos distinguen visualmente el tipo de cada componente tanto en la
   tabla global como en el modal de detalle.

## Alcance técnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `GET/POST /api/v1/equipos/componentes/`, `PATCH/DELETE /api/v1/equipos/componentes/{id}/` |
| Service | `backend/equipos/services/componente_service.py` |
| Repository | `backend/equipos/repositories/componente_repository.py` |
| Auditoría | `backend/shared/mixins/audit.py` (AuditableMixin) |
| Frontend | `ComponentesView.vue`, `EquipoDetailModal.vue`, `useComponentes.js` |

## RF / RNF relacionados

- RF: `docs/requerimientos-funcionales/equipos-componentes-hardware.md`

## Notas de implementación

- Los eventos de auditoría de componentes se registran sobre el **equipo padre**
  usando `ContentType.objects.get_for_model(equipo)` para que aparezcan en la
  línea de tiempo del equipo sin cambios en el frontend.
- El modal de equipo tiene 3 pestañas: Información, Componentes y Línea de
  Tiempo. La línea de tiempo carga de forma lazy al cambiar a esa pestaña.
- El select de equipos en el formulario global usa `/api/v1/equipos/opciones/`
  (sin paginar) para mostrar todos los equipos disponibles.
- `AuditableMixin` integrado también en `EquipoService` y `MantenimientoService`
  con eventos semánticos por campo (cambio de estado, espacio, responsable,
  técnicos asignados).

## Enlaces

- PR: https://github.com/Leonardo-Jaren/KairOs/pull/14
- Issue GitHub: https://github.com/Leonardo-Jaren/KairOs/issues/15
