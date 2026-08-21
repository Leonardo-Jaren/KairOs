# HU-SOFT-002: Gestionar instalaciones de software en equipos

Como administrador o técnico de KairOs, quiero registrar qué software está
instalado en cada equipo de cada espacio, para llevar el control de uso de
licencias y detectar vencimientos o sobre-uso a tiempo.

## Criterios de aceptación

1. Puedo ver las instalaciones de software filtrando por espacio, por equipo
   o por producto de software.
2. Puedo registrar una instalación indicando equipo, producto de software,
   número de licencia usado y fecha de instalación.
3. No puedo registrar una instalación si el producto ya no tiene licencias
   disponibles; el sistema me muestra un error.
4. No puedo duplicar la instalación del mismo producto en el mismo equipo.
5. Puedo editar el número de licencia usado y la fecha de instalación, pero
   no puedo cambiar el equipo ni el producto de una instalación existente.
6. Puedo eliminar una instalación (borrado lógico), lo que libera una
   licencia disponible del producto.
7. Como docente, puedo consultar las instalaciones pero no veo acciones de
   crear, editar ni eliminar.
8. Puedo ver estadísticas generales: total de instalaciones vigentes,
   productos con licencias próximas a expirar y productos sobre-utilizados.

## Alcance técnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `GET/POST /api/v1/software/instalaciones/`, `PATCH/DELETE /api/v1/software/instalaciones/{id}/` |
| API | `GET /api/v1/software/productos/estadisticas/` |
| Service | `backend/software/services/software_instalado_service.py` |
| Repository | `backend/software/repositories/software_instalado_repository.py` |
| Auditoría | `backend/shared/mixins/audit.py` (AuditableMixin) |

## RF / RNF relacionados

- RF: `docs/requerimientos-funcionales/software-gestionar-instalaciones.md`
- RNF: `docs/requerimientos-no-funcionales/software-gestionar-software.md`

## Notas de implementación

{Pendiente de completar al cerrar el desarrollo.}

## Enlaces

- PR: {URL del pull request}
- Issue GitHub: {URL del issue}
