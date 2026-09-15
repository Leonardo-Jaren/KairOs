# RF-ESPACIOS-03: Recorrer el mapa tecnológico por lugares

| Campo | Valor |
|-------|-------|
| Módulo | Espacios |
| Versión | 1.0 |
| Fecha | 2026-09-14 |
| Estado | En revisión |

## Propósito y alcance

`/espacios/mapa` facilita el acceso a la operación del campus a partir de su ubicación física: ciudad → local → pabellón → piso → ambiente → equipos. Desde el plano del ambiente se conservan los flujos existentes de componentes, software y mantenimiento. No se duplican esos módulos dentro del mapa.

Un local representa un recinto físico, por ejemplo el local central o La Esperanza. Una ciudad puede contener varios locales y cada local una cantidad distinta de pabellones. Los ejemplos proporcionados para verificar la navegación son Huánuco / Local central con un pabellón, Huánuco / La Esperanza con siete y un local de Tingo María con dos. Son escenarios de prueba, no datos que deban insertarse automáticamente ni reglas que limiten la cantidad de pabellones.

## Actores y precondiciones

- Administrador: consulta y administra locales, pabellones, ambientes y distribuciones.
- Técnico: consulta el mapa y usa las operaciones ya autorizadas en el detalle del ambiente.
- Se requiere una sesión válida y acceso al módulo Espacios. Los permisos se verifican también en la API.

## Flujo principal

1. Abrir el mapa y elegir la ciudad y el local.
2. Consultar los indicadores del local seleccionado y sus pabellones.
3. Si existe un solo pabellón, mostrar sus pisos directamente. Si hay varios, permitir cambiar de pabellón mediante controles legibles en escritorio y móvil.
4. Consultar el croquis existente del piso y abrir el plano de un ambiente.
5. Continuar en las operaciones existentes de equipos, componentes, software y mantenimiento desde ese ambiente.
6. Cambiar de local o pabellón conservando siempre un contexto coherente: no mostrar ambientes ni indicadores del lugar anterior.

## Administración y modelo de datos

- `Local` contiene código, nombre, ciudad, descripción y estado activo, además de los campos de auditoría compartidos.
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

## Criterios de aceptación

- Los escenarios de uno, siete y dos pabellones se presentan sin mezclar locales ni crear datos ficticios.
- Los indicadores y opciones de ambientes se calculan con el alcance del local seleccionado.
- Un local vacío no hereda el pabellón activo del local anterior.
- Los registros anteriores permanecen accesibles y pueden asignarse a un local.
- Los errores permiten reintento y las páginas adicionales de la API no se pierden.
- Un técnico no obtiene acciones administrativas ni puede ejecutarlas contra la API.
- Cambiar la asignación de un pabellón conserva su croquis y relaciones con ambientes.
- Se mantiene la distribución visual por pisos y los flujos operativos del plano.

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

Aplicar la nueva migración de Espacios antes de utilizar el frontend actualizado. Después, registrar los locales reales y asignar los pabellones existentes. Las verificaciones automáticas deben utilizar una base de prueba y datos aislados; no deben sembrar o reorganizar la base del usuario.

La migración `0008_local_edificio_local` se aplicó en el entorno de desarrollo durante esta implementación. No se crearon locales ni se asignaron pabellones automáticamente.

## Validación de la implementación

- Backend: 118 pruebas aprobadas, incluidas permisos, migración y preservación de croquis al reasignar.
- Frontend: 89 pruebas aprobadas, incluidas agrupación 1/7/2, local vacío, registros anteriores, paginación e historial de navegación.
- Revisión en navegador con datos aislados a 375, 1024 y 1600 píxeles: selectores, acciones administrativas, acceso del técnico, protección de edición y formulario de asignación.
- Los componentes y composables del croquis y plano originales permanecen sin modificaciones. El panel de pisos conserva su estructura y clases visuales; solo cambia la terminología de edificio a pabellón.

## Fuera de alcance

N/A para servicios externos. No se incluyen cartografía, coordenadas GPS, nuevos módulos operativos, cambios globales de tema ni rediseño del croquis por pisos.
