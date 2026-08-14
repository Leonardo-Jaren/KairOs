# HU-SOFTWARE-001: Administrar software instalado en una computadora

| Campo | Valor |
|-------|-------|
| Modulo | Software |
| Prioridad | Alta |
| Fecha | 2026-08-14 |
| Autor | Leonardo Jaren |
| Estado | En revision |

## Historia

**Como** administrador o tecnico  
**Quiero** consultar, instalar y retirar software en un equipo  
**Para** conocer su configuracion y controlar el uso de las licencias institucionales

## Descripcion

La ficha de cada computadora necesita mostrar su software real y permitir que los
roles operativos actualicen esa informacion sin perder la trazabilidad historica.

## Criterios de aceptacion

- [x] **Dado** un usuario sin rol operativo, **cuando** intenta consultar el modulo, **entonces** recibe una respuesta 403.
- [x] **Dado** un producto y equipo vigentes con licencia disponible, **cuando** se registra la instalacion, **entonces** aparece en el inventario del equipo.
- [x] **Dado** un producto ya instalado, **cuando** se intenta repetir la asignacion, **entonces** la API responde 400 sin duplicar registros.
- [x] **Dada** una instalacion vigente, **cuando** se retira, **entonces** deja de aparecer en las consultas y permanece almacenada como eliminada logicamente.
- [x] **Dada** una instalacion retirada, **cuando** se vuelve a instalar el mismo producto, **entonces** se reactiva el registro anterior.

## Alcance tecnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `GET /api/v1/software/productos/` |
| API | `GET, POST /api/v1/software/instalaciones/` |
| API | `DELETE /api/v1/software/instalaciones/{id}/` |
| Service | `backend/software/services/` |
| Repository | `backend/software/repositories/` |

## RF / RNF relacionados

- RF: `RF-SOFTWARE-001`
- RNF: N/A

## Notas de implementacion

Se reutilizan los campos actuales de version, tipo de licencia, cantidad total,
expiracion, numero de licencia y fecha de instalacion. No se requiere migracion.

## Enlaces

- PR: N/A
- Issue GitHub: N/A
