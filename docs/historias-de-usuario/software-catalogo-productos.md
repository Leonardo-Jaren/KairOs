# HU-SOFT-001: Gestionar catálogo de productos de software

Como administrador o técnico de KairOs, quiero registrar y mantener
actualizado el catálogo de productos de software (versión, tipo de licencia,
licencias totales, fecha de expiración y costo anual) para tener control
centralizado de las licencias disponibles en la institución.

## Criterios de aceptación

1. Puedo ver todos los productos de software en `/software`, con licencias
   totales, usadas y disponibles visibles en la tabla, y filtros por texto y
   tipo de licencia.
2. Puedo agregar un producto indicando software, versión, tipo de licencia,
   licencias totales y, opcionalmente, descripción, fecha de expiración y
   costo anual.
3. No puedo registrar dos productos con el mismo nombre y versión.
4. Puedo editar los datos de un producto existente, incluyendo aumentar sus
   licencias totales.
5. No puedo eliminar un producto que tenga instalaciones vigentes.
6. Puedo ver, desde el detalle de un producto, en qué equipos está instalado.
7. Como docente, puedo consultar el catálogo pero no veo acciones de crear,
   editar ni eliminar.
8. Veo un indicador cuando un producto tiene licencias próximas a expirar o
   sobre-utilizadas.

## Alcance técnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `GET/POST /api/v1/software/productos/`, `PATCH/DELETE /api/v1/software/productos/{id}/` |
| Service | `backend/software/services/producto_software_service.py` |
| Repository | `backend/software/repositories/producto_software_repository.py` |
| Auditoría | `backend/shared/mixins/audit.py` (AuditableMixin) |

## RF / RNF relacionados

- RF: `docs/requerimientos-funcionales/software-catalogo-productos.md`
- RNF: `docs/requerimientos-no-funcionales/software-gestionar-software.md`

## Notas de implementación

{Pendiente de completar al cerrar el desarrollo.}

## Enlaces

- PR: {URL del pull request}
- Issue GitHub: {URL del issue}
