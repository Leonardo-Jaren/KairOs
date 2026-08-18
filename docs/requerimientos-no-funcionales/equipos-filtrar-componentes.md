# RNF-EQUIPOS-004: Consistencia del listado de componentes

| Campo | Valor |
|-------|-------|
| Modulo | Equipos |
| Categoria | Usabilidad / Mantenibilidad |
| Fecha | 2026-08-17 |
| Autor | Leonardo Jaren |
| Estado | En revision |

## Descripcion

La interfaz debe mantener consistencia entre la respuesta de edicion, la fila mostrada y el total paginado del backend.

## Justificacion

Una recarga inmediata ordenada por tipo puede mover el registro a otra pagina y hacer parecer que la edicion no fue aplicada.

## Metrica / umbral

| Metrica | Valor objetivo |
|---------|----------------|
| Registros por pagina | 10 |
| Confirmacion visual de una edicion | Inmediata tras la respuesta exitosa |

## Implementacion esperada

- Aplicar filtros en Repository y propagarlos mediante Service y ViewSet.
- Reutilizar el componente compartido de paginacion.
- Sustituir la entidad editada usando la representacion devuelta por la API.

## Verificacion

- [x] Pruebas API de busqueda y filtro por tipo.
- [x] Pruebas frontend de paginacion y sustitucion tras editar.
- [x] Build de produccion.

## Relacion con RF

- RF relacionados: RF-EQUIPOS-004

## Notas

N/A
