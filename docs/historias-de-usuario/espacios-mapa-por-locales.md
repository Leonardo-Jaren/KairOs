# HU-ESPACIOS-03: Ubicar la operación por ciudad y local

| Campo | Valor |
|-------|-------|
| Módulo | Espacios |
| Prioridad | Alta |
| Fecha | 2026-09-14 |
| Estado | En revisión |

## Historia

**Como** administrador o técnico, **quiero** elegir una ciudad, un local y su pabellón antes de recorrer pisos y ambientes, **para** trabajar con los equipos del lugar correcto desde el mapa tecnológico.

## Descripción

La navegación debe responder a la estructura real de cada local, tanto si contiene un pabellón como si contiene varios. El croquis por pisos y el plano de equipos mantienen su diseño y operaciones actuales. El mapa organiza el acceso a esas operaciones sin duplicar los demás módulos.

## Criterios de aceptación

- Dado un local con un pabellón, al elegirlo se muestran sus pisos directamente.
- Dado un local con siete pabellones, al elegirlo aparecen únicamente sus pabellones y sus indicadores.
- Dado otro local de Tingo María con dos pabellones, al cambiar de ciudad y local no quedan ambientes del lugar anterior.
- Dado un local vacío, se muestra una invitación a agregar un pabellón para el administrador.
- Dado un pabellón anterior sin ubicación, se puede consultar en Sin local asignado y asignarlo mediante su formulario.
- Dado un croquis en edición, un cambio de contexto no descarta el trabajo sin guardarlo o cancelarlo.
- Dado un técnico, la consulta está disponible y la API rechaza escrituras de locales y pabellones.
- Dado un local con pabellones vinculados, no se puede desactivar hasta resolver sus asignaciones.

## Alcance técnico

Modelo `Local` y relación opcional `Edificio.local`; CRUD de locales mediante capas compartidas; selección territorial, formularios y conteos en composables de Espacios; componentes de navegación separados del croquis existente; pruebas de permisos, persistencia, aislamiento y regresión del mapa.

## RF / RNF relacionados

- RF: [RF-ESPACIOS-03](../requerimientos-funcionales/espacios-mapa-por-locales.md).
- RF previo: [RF-ESPACIOS-02](../requerimientos-funcionales/espacios-plano-interactivo.md).
- RNF: se mantienen autenticación, autorización y arquitectura establecidas en el proyecto; no se introduce un servicio externo.

## Notas de implementación

La migración conserva los datos existentes sin inferir ubicaciones. Los escenarios territoriales se usan como datos aislados de prueba. Los locales reales se registran y sus pabellones se asignan desde la interfaz después de aplicar la migración.

## Enlaces

- PR: N/A.
- Issue GitHub: N/A.
