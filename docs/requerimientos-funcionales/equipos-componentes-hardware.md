# RF-EQUI-002: Gestionar componentes de hardware de un equipo

## Descripción

El sistema debe permitir registrar, consultar, editar y eliminar los
componentes de hardware (CPU, RAM, SSD, GPU, etc.) asociados a cada equipo del
inventario, manteniendo trazabilidad de auditoría sobre cada cambio.

## Criterios funcionales

- Solo administradores y técnicos pueden crear, editar y eliminar componentes.
- Cada componente está asociado obligatoriamente a un equipo existente y no
  puede cambiar de equipo una vez creado.
- El tipo de componente admite: CPU, RAM, SSD, HDD, GPU, Motherboard, Fuente
  de Poder, Tarjeta de Red y Otro.
- Los campos requeridos son tipo y modelo; la descripción es opcional.
- El listado global (`/componentes`) muestra todos los componentes con filtros
  rápidos por tipo y búsqueda de texto.
- El detalle de un equipo incluye una pestaña "Componentes" con CRUD inline y
  una pestaña "Línea de Tiempo" con el historial de auditoría del equipo.
- Cada alta, modificación y baja de componente genera un evento de auditoría
  registrado sobre el equipo padre (eventos `equipo.componente_agregado`,
  `equipo.componente_modificado`, `equipo.componente_eliminado`).
- La eliminación es un borrado lógico (`is_deleted=True`).

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET /api/v1/equipos/componentes/` |
| API | `POST /api/v1/equipos/componentes/` |
| API | `PATCH /api/v1/equipos/componentes/{id}/` |
| API | `DELETE /api/v1/equipos/componentes/{id}/` |
| Backend | `backend/equipos/repositories/componente_repository.py` |
| Backend | `backend/equipos/services/componente_service.py` |
| Backend | `backend/equipos/serializers/componente_serializers.py` |
| Backend | `backend/equipos/views/componente_views.py` |
| Frontend | `frontend/src/views/equipos/ComponentesView.vue` |
| Frontend | `frontend/src/components/equipos/EquipoDetailModal.vue` |
| Frontend | `frontend/src/composables/equipos/useComponentes.js` |
| Frontend | `frontend/src/services/componentes.service.js` |
