# RF-ESPACIOS-03: Recorrer el mapa tecnológico por lugares

| Campo | Valor |
|-------|-------|
| Módulo | Espacios |
| Versión | 2.1 |
| Fecha | 2026-09-26 |
| Estado | En revisión |

## Propósito y alcance

`/espacios/mapa` conserva el mapa departamental interactivo para elegir una ciudad y facilita el recorrido por la jerarquía ciudad → local → pabellón → piso → ambiente → equipos. Después de elegir una ciudad, sus locales se presentan como módulos axonométricos conectados a la ciudad. El diagrama expresa relaciones jerárquicas y no ubicaciones, distancias ni coordenadas geográficas. Desde el plano del ambiente se conservan los flujos existentes de componentes, software y mantenimiento. No se duplican esos módulos dentro del mapa.

Un local representa un recinto físico, por ejemplo el campus central o una sede. Una ciudad puede contener varios locales y cada local una cantidad distinta de pabellones. El comando opcional `seed_datos_prueba` crea cuatro locales demostrativos y reparte ocho pabellones entre ellos para verificar el aislamiento visual. Son escenarios de prueba y no reglas que limiten la cantidad de pabellones.

## Actores y precondiciones

- Administrador: consulta y administra locales, pabellones, ambientes y distribuciones.
- Técnico: consulta el mapa y usa las operaciones ya autorizadas en el detalle del ambiente.
- Se requiere una sesión válida y acceso al módulo Espacios. Los permisos se verifican también en la API.

## Flujo principal

1. Abrir el mapa departamental existente y elegir una ciudad.
2. Consultar las sedes de esa ciudad en el diagrama axonométrico, conectadas visualmente con la ciudad elegida.
3. Si hay más de tres sedes, recorrerlas en páginas de hasta tres módulos; la búsqueda filtra los resultados y vuelve a la primera página.
4. Elegir una sede y luego el pabellón, sin autoseleccionar silenciosamente opciones posteriores.
5. Elegir un piso en el selector visual y consultar su croquis existente.
6. Abrir el plano de un ambiente y continuar en las operaciones existentes de equipos, componentes, software y mantenimiento.
7. Cambiar cualquier nivel conservando un contexto coherente y limpiando las selecciones descendientes.

## Administración y modelo de datos

- `Ciudad` es una entidad de catálogo independiente. Cada local referencia una ciudad mediante `ciudad_id`; las respuestas conservan `ciudad` como nombre de presentación y también exponen `ciudad_id`.
- El nombre normalizado de ciudad es único, ignorando tildes, mayúsculas y espacios repetidos. La migración agrupa los textos existentes equivalentes y conserva una etiqueta legible.
- `Local` contiene código, nombre, referencia a ciudad, tipo de ubicación, descripción y estado activo, además de los campos de auditoría compartidos.
- El tipo de ubicación usa los valores estables `campus`, `sede`, `anexo` y `otro`. Los registros existentes migran como `sede` para conservar compatibilidad.
- `Edificio` sigue siendo la entidad interna del pabellón. Se añade la relación opcional `local`, expuesta como `local_id` y un resumen de lectura.
- El administrador selecciona una ciudad existente al crear o editar un local. La ciudad se crea desde el catálogo; no se admite texto libre como identificador al registrar un local.
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
- El mapa departamental inicial y su selección de ciudades se conservan sin cambios.
- Después de seleccionar una ciudad, cada local se presenta como un módulo axonométrico seleccionable conectado con la ciudad; el diagrama no asigna coordenadas ni distancias físicas.
- El diagrama muestra hasta tres locales por página y ofrece paginación cuando hay más; en pantallas pequeñas apila los módulos verticalmente.
- Seleccionar un módulo conserva el identificador y el flujo de navegación existentes para abrir el local y sus pabellones.
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
| API | `GET, POST /api/v1/espacios/ciudades/` |
| API | `/api/v1/espacios/edificios/`, con `local_id` en escritura y filtro de listado |
| Vista | `frontend/src/views/espacios/CampusTecnologicoView.vue` |
| Lógica | `frontend/src/composables/espacios/useCampusTecnologico.js` |
| Modelos | `backend/espacios/models.py` |
| Flujo previo | [RF-ESPACIOS-02](espacios-plano-interactivo.md) |

## Activación

Aplicar la nueva migración de Espacios antes de utilizar el frontend actualizado. La migración genera el catálogo a partir de las ciudades guardadas en los locales y combina nombres equivalentes; después se pueden crear más ciudades y locales desde la interfaz. El comando `seed_datos_prueba` se ejecuta solo de forma explícita en desarrollo o demostraciones.

Las migraciones `0008_local_edificio_local`, `0009_local_tipo` y `0013_ciudad_catalogo` deben aplicarse antes de usar el flujo actualizado. La migración de ciudad no crea locales ni asigna pabellones.

## Validación de la implementación

- Backend: 118 pruebas aprobadas, incluidas permisos, migración y preservación de croquis al reasignar.
- Frontend: 379 pruebas aprobadas en la suite, incluidas las regresiones del mapa de ciudades y las pruebas de selección, búsqueda y paginación del esquema axonométrico.
- Build de producción verificado y revisión visual en navegador de la ruta, selectores, métricas, pabellones y pisos con datos reales.
- Se conserva el croquis y su lógica de distribución. El navegador de pisos se extrae a un componente reutilizable y el enlace al detalle mantiene el contexto completo del mapa.

## Fuera de alcance

N/A para servicios externos. No se incluyen cartografía, coordenadas GPS, nuevos módulos operativos, cambios globales de tema ni rediseño del croquis por pisos.
