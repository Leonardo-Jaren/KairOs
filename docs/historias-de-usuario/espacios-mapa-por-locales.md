# HU-ESPACIOS-03: Ubicar la operación por ciudad y local

| Campo | Valor |
|-------|-------|
| Módulo | Espacios |
| Prioridad | Alta |
| Fecha | 2026-09-26 |
| Estado | En revisión |

## Historia

**Como** administrador o técnico, **quiero** elegir una ciudad y abrir sus sedes desde un esquema axonométrico conectado, **para** recorrer la jerarquía de espacios sin confundirla con ubicaciones geográficas exactas.

## Descripción

El mapa departamental y la selección de ciudades mantienen su presentación actual. Después de elegir una ciudad, sus sedes se muestran como módulos axonométricos conectados a la ciudad; la disposición representa la jerarquía, no una ubicación física ni coordenadas. El croquis por pisos y el plano de equipos mantienen su diseño y operaciones actuales. El esquema organiza el acceso a esas operaciones sin duplicar los demás módulos ni requerir datos geográficos nuevos.

## Criterios de aceptación

- Dado un local con un pabellón, al elegirlo se muestran sus pisos directamente.
- Dado un local con siete pabellones, al elegirlo aparecen únicamente sus pabellones y sus indicadores.
- Dada una ciudad, el mapa departamental existente permanece intacto; sus sedes se muestran después como módulos conectados y seleccionables.
- Dada una ciudad con más de tres sedes, el esquema pagina los módulos en grupos de hasta tres y la búsqueda permite encontrarlos.
- Dado un dispositivo estrecho, los módulos se apilan verticalmente y siguen siendo seleccionables con teclado y pantalla táctil.
- Dado un esquema axonométrico, sus posiciones no se interpretan como coordenadas, orientación ni distancia entre sedes.
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
