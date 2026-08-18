# HU-EQUIPOS-004: Editar componentes sin perder el resultado

| Campo | Valor |
|-------|-------|
| Modulo | Equipos |
| Prioridad | Alta |
| Fecha | 2026-08-17 |
| Autor | Leonardo Jaren |
| Estado | En revision |

## Historia

**Como** administrador del inventario
**Quiero** editar y localizar componentes sobre el listado completo
**Para** confirmar que los cambios se aplicaron correctamente

## Descripcion

El listado anterior cargaba solo la primera pagina y la recargaba despues de editar. Si cambiaba el tipo, el ordenamiento podia mover el registro y ocultar el resultado actualizado.

## Criterios de aceptacion

- [x] **Dado** un componente visible, **cuando** edito su tipo, **entonces** la fila refleja la respuesta actualizada.
- [x] **Dado** un inventario paginado, **cuando** busco un modelo, **entonces** se consulta el conjunto completo.
- [x] El usuario puede navegar entre todas las paginas de componentes.

## Alcance tecnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `GET /api/v1/equipos/componentes/` |
| Service | `backend/equipos/services/componente_service.py` |
| Repository | `backend/equipos/repositories/componente_repository.py` |
| Frontend | `frontend/src/composables/equipos/useComponentes.js` |

## RF / RNF relacionados

- RF: `RF-EQUIPOS-004`
- RNF: `RNF-EQUIPOS-004`

## Notas de implementacion

Se agregaron filtros server-side, paginacion visible y actualizacion local con la respuesta serializada.

## Enlaces

- PR: https://github.com/Leonardo-Jaren/KairOs/pull/21
- Issue GitHub: https://github.com/Leonardo-Jaren/KairOs/issues/22
