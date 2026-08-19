# RF-SOFTWARE-001: Gestionar software instalado por equipo

| Campo | Valor |
|-------|-------|
| Modulo | Software |
| Version | 1.0 |
| Fecha | 2026-08-14 |
| Autor | Leonardo Jaren |
| Estado | En revision |

## Descripcion

El sistema permite consultar el catalogo vigente y gestionar las instalaciones
de productos de software en cada equipo institucional.

## Actores

- Administrador
- Tecnico

## Precondiciones

- El actor inicio sesion con rol administrador o tecnico.
- El equipo y el producto de software se encuentran vigentes.

## Flujo principal

1. El actor consulta el catalogo de productos y su disponibilidad de licencias.
2. El actor selecciona un equipo, un producto, la fecha de instalacion y, si corresponde, el numero de licencia.
3. El sistema valida la asignacion, registra la instalacion y la muestra en el inventario del equipo.
4. El actor puede retirar posteriormente la instalacion sin eliminar su historial.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Producto duplicado en el equipo | La API rechaza la asignacion con un error asociado al producto. |
| Licencias agotadas o expiradas | La API no registra la instalacion e informa la causa. |
| Equipo o producto retirado | La API rechaza la relacion como no vigente. |
| Reinstalacion previamente retirada | El sistema reactiva el mismo registro conservando su identidad. |

## Reglas de negocio

- Solo administradores y tecnicos pueden consultar o gestionar instalaciones.
- Un producto solo puede tener una instalacion vigente por equipo.
- Los productos con licencia libre no tienen limite de instalaciones.
- Los demas productos no pueden superar `licencias_totales` ni instalarse luego de su expiracion.
- La fecha de instalacion no puede ser posterior a la fecha actual.
- El retiro es logico y conserva la trazabilidad de auditoria.

## Criterios de aceptacion

- [x] El catalogo informa licencias usadas y disponibles sin contar instalaciones retiradas.
- [x] Las instalaciones pueden consultarse filtrando por `equipo_id`.
- [x] Una instalacion valida se crea con el usuario autenticado como autor.
- [x] Los duplicados, relaciones retiradas y licencias no disponibles retornan error 400.
- [x] El retiro oculta la instalacion y permite reinstalar el producto posteriormente.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET /api/v1/software/productos/` |
| API | `GET, POST /api/v1/software/instalaciones/` |
| API | `DELETE /api/v1/software/instalaciones/{id}/` |
| Backend | `backend/software/` |

## Notas

Los eventos de instalacion y retiro se registran sobre el equipo para que formen
parte de su linea de tiempo operativa.
