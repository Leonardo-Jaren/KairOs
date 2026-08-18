# RF-NAVEGACION-001: Colapsar la barra lateral

| Campo | Valor |
|-------|-------|
| Modulo | Navegacion |
| Version | 1.0 |
| Fecha | 2026-08-17 |
| Autor | Leonardo Jaren |
| Estado | En revision |

## Descripcion

El usuario puede reducir y restaurar la barra lateral desde el control ubicado en su parte superior.

## Actores

- Usuario autenticado

## Precondiciones

- El usuario accedio a una vista que utiliza el panel administrativo.

## Flujo principal

1. El usuario pulsa el control de contraccion en el encabezado de la barra lateral.
2. La barra reduce su ancho con una transicion breve y conserva visibles los iconos de los modulos.
3. El usuario pulsa el mismo control para restaurar la barra completa.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Vista movil | La barra se oculta y puede abrirse nuevamente con el boton de menu existente. |
| Cambio de ruta en movil | La barra se cierra automaticamente. |

## Reglas de negocio

- El cierre no modifica la sesion ni la ruta activa.
- La barra compacta debe conservar los accesos mediante iconos y ayudas de texto.
- Siempre debe existir un control accesible para restaurar su ancho completo.

## Criterios de aceptacion

- [x] La barra lateral se puede reducir desde su encabezado sin desaparecer.
- [x] Los iconos de navegacion permanecen disponibles en el estado compacto.
- [x] La barra lateral se puede restaurar desde el mismo control superior.
- [x] Los controles cuentan con nombre accesible y estado de foco visible.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| Frontend | `frontend/src/layouts/DashboardLayout.vue` |
| Prueba | `frontend/src/layouts/DashboardLayout.spec.js` |

## Notas

No requiere cambios en la API.
