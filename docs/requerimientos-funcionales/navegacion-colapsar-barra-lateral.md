# RF-NAVEGACION-001: Colapsar la barra lateral

| Campo | Valor |
|-------|-------|
| Modulo | Navegacion |
| Version | 1.0 |
| Fecha | 2026-08-17 |
| Autor | Leonardo Jaren |
| Estado | En revision |

## Descripcion

El usuario puede ocultar y restaurar la barra lateral desde controles ubicados en la parte superior de la interfaz.

## Actores

- Usuario autenticado

## Precondiciones

- El usuario accedio a una vista que utiliza el panel administrativo.

## Flujo principal

1. El usuario pulsa el control de cierre en el encabezado de la barra lateral.
2. La barra se oculta con una transicion breve y el contenido aprovecha el espacio disponible.
3. El usuario pulsa el control de apertura del encabezado principal para restaurarla.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Vista movil | La barra se cierra y puede abrirse nuevamente con el boton de menu existente. |
| Cambio de ruta en movil | La barra se cierra automaticamente. |

## Reglas de negocio

- El cierre no modifica la sesion ni la ruta activa.
- Siempre debe existir un control accesible para restaurar la barra.

## Criterios de aceptacion

- [x] La barra lateral se puede cerrar desde su encabezado.
- [x] La barra lateral se puede restaurar desde el encabezado principal.
- [x] Los controles cuentan con nombre accesible y estado de foco visible.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| Frontend | `frontend/src/layouts/DashboardLayout.vue` |
| Prueba | `frontend/src/layouts/DashboardLayout.spec.js` |

## Notas

No requiere cambios en la API.
