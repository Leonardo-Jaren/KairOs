# RF-ESPACIOS-03: Recorrer el mapa tecnológico por lugares

| Campo | Valor |
|-------|-------|
| Módulo | Espacios |
| Versión | 2.0 |
| Fecha | 2026-09-18 |
| Estado | En revisión |

## Propósito y alcance

`/espacios/mapa` facilita el acceso a la operación del campus a partir de su ubicación física: ciudad → tipo de ubicación → local → pabellón → piso → ambiente → equipos. Desde el plano del ambiente se conservan los flujos existentes de componentes, software y mantenimiento. No se duplican esos módulos dentro del mapa.

Un local representa un recinto físico, por ejemplo el campus central o una sede. Una ciudad puede contener varios locales y cada local una cantidad distinta de pabellones. El comando opcional `seed_datos_prueba` crea cuatro locales demostrativos y reparte ocho pabellones entre ellos para verificar el aislamiento visual. Son escenarios de prueba y no reglas que limiten la cantidad de pabellones.

## Actores y precondiciones

- Administrador: consulta y administra locales, pabellones, ambientes y distribuciones.
- Técnico: consulta el mapa y usa las operaciones ya autorizadas en el detalle del ambiente.
- Se requiere una sesión válida y acceso al módulo Espacios. Los permisos se verifican también en la API.

## Flujo principal

1. Abrir el mapa y elegir la ciudad.
2. Elegir el tipo de ubicación disponible en la ciudad: campus, sede, anexo u otro.
3. Elegir el local y luego el pabellón, sin autoseleccionar silenciosamente opciones posteriores.
4. Elegir un piso en el selector visual y consultar su croquis existente.
5. Abrir el plano de un ambiente y continuar en las operaciones existentes de equipos, componentes, software y mantenimiento.
6. Cambiar cualquier nivel conservando un contexto coherente y limpiando las selecciones descendientes.

## Administración y modelo de datos

- `Local` contiene código, nombre, ciudad, tipo de ubicación, descripción y estado activo, además de los campos de auditoría compartidos.
- El tipo de ubicación usa los valores estables `campus`, `sede`, `anexo` y `otro`. Los registros existentes migran como `sede` para conservar compatibilidad.
- La ciudad se registra como texto del local; no se agrega un catálogo geográfico ni un mapa cartográfico.
- `Edificio` sigue siendo la entidad interna del pabellón. Se añade la relación opcional `local`, expuesta como `local_id` y un resumen de lectura.
- El administrador crea y edita locales, y asigna o reasigna pabellones usando su identificador, nunca mediante coincidencias del nombre.
- Los nombres de pabellón pueden repetirse entre locales; los códigos conservan la unicidad global del contrato existente.
- La relación de un ambiente sigue siendo `Espacio.edificio`. No se duplica `local_id` en los ambientes.
- No se puede desactivar un local que todavía contiene pabellones no eliminados, aunque estén inactivos. Se deben reasignar o retirar primero. Se aplica tanto a `DELETE` como a `PATCH activo=false`.
- Solo se pueden hacer nuevas asignaciones a locales activos y no eliminados.

## Compatibilidad y zona protegida

La migración es aditiva: los pabellones existentes quedan sin local asignado. Se mantienen sus identificadores, ambientes, equipos, historial y `configuracion_croquis`. No se adivina su ubicación ni se modifican las distribuciones guardadas.

La interfaz ofrece el grupo **Sin local asignado** para consultar y clasificar esos pabellones. El administrador puede abrir su edición y seleccionar el local correcto.

Se conserva el diseño de **Pisos y ambientes**, incluida la distribución visual de aulas, laboratorios, oficinas, pasillos, colores operativos y controles del croquis. No se rediseñan `CroquisPiso.vue`, `useCroquisPiso.js`, el plano interno ni el detalle de los ambientes. Los cambios de terminología y contexto exterior no deben alterar esa representación.

## Excepciones y navegación

| Caso | Comportamiento esperado |
|------|-------------------------|
| No existen locales | Ofrecer registro al administrador y mantener acceso a pabellones sin asignar. |
| Local sin pabellones | Mostrar estado vacío del local y acción contextual para agregar uno. |
| Pabellón sin ambientes | Mantener el estado vacío existente y permitir agregar un ambiente. |
| Error de API | Mostrar error y reintento; no presentar el fallo como ausencia de registros. |
| Listado paginado | Recuperar todas las páginas necesarias antes de calcular los indicadores. |
| Croquis en edición | Impedir cambios de contexto que descarten el borrador y explicar que se debe guardar o cancelar. |
| Identificador inválido o pabellón de otro local | Resolver una selección coherente, sin mezclar lugares. |
| Enlace anterior con `legacy`, `**legacy**` o `__legacy__` | Resolverlo como registros pendientes de clasificación sin exponer el sentinel técnico. |

## Criterios de aceptación

- Los pabellones se presentan únicamente dentro del local al que pertenecen, sin mezclar ciudades o tipos de ubicación.
- Los indicadores y opciones de ambientes se calculan con el alcance del local seleccionado.
- Un local vacío no hereda el pabellón activo del local anterior.
- Los registros anteriores permanecen accesibles y pueden asignarse a un local.
- Los errores permiten reintento y las páginas adicionales de la API no se pierden.
- Un técnico no obtiene acciones administrativas ni puede ejecutarlas contra la API.
- Cambiar la asignación de un pabellón conserva su croquis y relaciones con ambientes.
- Se mantiene la distribución visual por pisos y los flujos operativos del plano.
- La URL conserva `ciudad`, `tipo`, `local`, `pabellon` y `piso`; al abrir un ambiente y volver se restaura el mismo contexto.

## Contratos y archivos de referencia

| Tipo | Ruta |
|------|------|
| API | `GET, POST /api/v1/espacios/locales/` |
| API | `GET, PATCH, DELETE /api/v1/espacios/locales/{id}/` |
| API | `/api/v1/espacios/edificios/`, con `local_id` en escritura y filtro de listado |
| Vista | `frontend/src/views/espacios/CampusTecnologicoView.vue` |
| Lógica | `frontend/src/composables/espacios/useCampusTecnologico.js` |
| Modelos | `backend/espacios/models.py` |
| Flujo previo | [RF-ESPACIOS-02](espacios-plano-interactivo.md) |

## Activación

Aplicar la nueva migración de Espacios antes de utilizar el frontend actualizado. Después, registrar los locales reales y asignar los pabellones existentes. En una instalación real la migración no crea datos: el sistema comienza vacío y todo se registra manualmente. El comando `seed_datos_prueba` se ejecuta solo de forma explícita en desarrollo o demostraciones.

Las migraciones `0008_local_edificio_local` y `0009_local_tipo` deben aplicarse antes de usar el flujo actualizado. No se crean locales ni se asignan pabellones automáticamente mediante migraciones.

## Validación de la implementación

- Backend: 118 pruebas aprobadas, incluidas permisos, migración y preservación de croquis al reasignar.
- Frontend: 91 pruebas aprobadas, incluida la nueva cascada ciudad → tipo → local → pabellón y la regresión del selector de pisos sin desplazamiento horizontal, además de local vacío, registros anteriores, paginación e historial de navegación.
- Build de producción verificado y revisión visual en navegador de la ruta, selectores, métricas, pabellones y pisos con datos reales.
- Se conserva el croquis y su lógica de distribución. El navegador de pisos se extrae a un componente reutilizable y el enlace al detalle mantiene el contexto completo del mapa.

## Fuera de alcance

N/A para servicios externos. No se incluyen cartografía, coordenadas GPS, nuevos módulos operativos, cambios globales de tema ni rediseño del croquis por pisos.
