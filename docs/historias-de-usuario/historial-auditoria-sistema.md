# HU-HISTORIAL-001: Registrar y visualizar historial de auditoría del sistema

| Campo | Valor |
|-------|-------|
| Módulo | Historial |
| Prioridad | Alta |
| Fecha | 2026-08-03 |
| Autor | Marcel Trujillo |
| Estado | En revisión |

## Historia

**Como** administrador o técnico de KairOs
**Quiero** ver el historial completo de cambios realizados sobre las entidades del sistema
**Para** tener trazabilidad de todas las operaciones y poder auditar quién hizo qué y cuándo

## Descripción

Se implementó un módulo de auditoría global compuesto por un backend que registra eventos CRUD en todos los módulos del sistema, y un frontend que permite visualizar dichos eventos en una vista de historial general y en un timeline por entidad accesible desde cualquier módulo.

El registro de auditoría es automático mediante `AuditableMixin` en `shared/`, de modo que los módulos futuros solo heredan el mixin sin escribir código de auditoría adicional.

## Criterios de aceptación

- [x] **Dado** un administrador autenticado, **cuando** crea, edita o desactiva un usuario, **entonces** se genera un evento de auditoría con el tipo, descripción, actor y fecha correspondientes.
- [x] **Dado** un cambio de campo (ej. DNI, nombre, rol), **cuando** se guarda la actualización, **entonces** el historial registra los valores antes y después del cambio.
- [x] **Dado** un administrador o técnico, **cuando** accede a `/historial`, **entonces** ve la lista paginada de eventos con filtros por módulo, tipo de evento y fecha.
- [x] **Dado** un evento con cambios de campo, **cuando** el usuario hace clic en "Detalles", **entonces** se abre un modal con pestañas: Información (antes/después) y Línea de Tiempo (eventos de esa entidad).
- [x] **Dado** cualquier vista de entidad (ej. usuarios), **cuando** el usuario hace clic en el ícono de ojo, **entonces** se abre `EntityDetailModal` con los datos de la entidad y su línea de tiempo de auditoría.

## Alcance técnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `GET /api/v1/historial/` |
| Model | `backend/historial/models.py` |
| Service | `backend/historial/services/historial_service.py` |
| Repository | `backend/historial/repositories/historial_repository.py` |
| Mixin compartido | `backend/shared/mixins/audit.py` |
| Servicios migrados | `backend/usuarios/services/usuario_service.py`, `backend/espacios/services/espacio_service.py`, `backend/espacios/services/espacio_usuario_service.py` |
| Frontend vista | `frontend/src/views/historial/HistorialView.vue` |
| Frontend componentes | `frontend/src/components/historial/`, `frontend/src/components/shared/EntityDetailModal.vue` |
| Frontend composable | `frontend/src/composables/historial/useHistorial.js` |
| Frontend servicio | `frontend/src/services/historial.service.js` |

## RF / RNF relacionados

- RF: N/A
- RNF: N/A

## Notas de implementación

- `AuditableMixin` implementa el patrón de hooks (`_do_create`, `_do_update`, `_do_delete`) separando lógica de negocio de auditoría. Los servicios simples heredan el mixin sin cambios; los complejos sobreescriben solo los hooks `_do_*`.
- `EntityDetailModal` es un componente compartido reutilizable: recibe `modulo` y `object-id` y carga automáticamente el timeline; cada vista aporta sus campos propios vía slot `#info`.
- Los eventos `usuario.cambio_rol` y `usuario.actualizacion` se generan por separado para distinguir cambios semánticos (rol) de cambios generales de datos.

## Enlaces

- PR: pendiente
- Issue GitHub: pendiente
