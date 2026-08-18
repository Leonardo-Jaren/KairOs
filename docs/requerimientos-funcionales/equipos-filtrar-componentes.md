# RF-EQUIPOS-004: Consultar y editar componentes paginados

| Campo | Valor |
|-------|-------|
| Modulo | Equipos |
| Version | 1.0 |
| Fecha | 2026-08-17 |
| Autor | Leonardo Jaren |
| Estado | En revision |

## Descripcion

El listado global de componentes debe consultar, filtrar y paginar el inventario completo, además de reflejar inmediatamente una edición confirmada por la API.

## Actores

- Administrador
- Tecnico

## Precondiciones

- El usuario se encuentra autenticado y tiene acceso al modulo de componentes.

## Flujo principal

1. El usuario busca, filtra o cambia de pagina en el listado.
2. El frontend envia los parametros al endpoint de componentes.
3. El backend filtra el conjunto completo antes de paginarlo.
4. Al editar, la respuesta actualizada sustituye inmediatamente la fila visible.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Sin coincidencias | Se presenta el estado vacio de la tabla. |
| Error de API | Se conserva la informacion visible y se muestra una notificacion de error. |

## Reglas de negocio

- La busqueda considera modelo, descripcion y codigo del equipo.
- El filtro por tipo se aplica antes de calcular la cantidad de paginas.
- La edicion no cambia el equipo asociado al componente.

## Criterios de aceptacion

- [x] La busqueda consulta todos los componentes y no solo la primera pagina.
- [x] El listado permite navegar por todas las paginas disponibles.
- [x] Una edicion exitosa actualiza inmediatamente tipo, modelo y descripcion visibles.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET /api/v1/equipos/componentes/` |
| Backend | `backend/equipos/` |
| Frontend | `frontend/src/views/equipos/ComponentesView.vue` |

## Notas

No requiere migraciones.
