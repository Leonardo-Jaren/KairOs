# Revisión visual de Espacios

Capturas generadas con la interfaz real de Vue/Tailwind en `localhost:5173` y una sesión de prueba con datos simulados. **No son capturas de los datos de producción.** No se guardaron credenciales ni respuestas reales del backend.

Se revisaron tres tamaños: escritorio (1440 × 900), móvil (375 × 812) y móvil estrecho (320 × 740). Para cada tamaño hay capturas de Mapa (ciudades, locales, pabellones, pisos y plano del piso), Tradicional (ciudades, locales, pabellones, pisos y piso seleccionado), y Lista (global y filtrada por local). Las capturas con el prefijo `mobile-`, `desktop-` o `small-` muestran cada pantalla completa. Los mosaicos resumen nueve estados principales; los pisos profundos están en los archivos individuales `*-map-pisos.png`, `*-map-plano.png` y `*-trad-piso-seleccionado.png`.

Vistas generales:

- [Recorrido móvil](mobile-resumen.png)
- [Recorrido de escritorio](desktop-resumen.png)

En Tradicional se muestra directamente el croquis de cada piso al abrir un pabellón, sin modal intermedio. La edición de la distribución sigue disponible mediante «Editar distribución en Mapa».

También se verificó el enlace directo con `piso=2`, el cambio Mapa → Tradicional → Mapa y el enlace desde el croquis al editor en Mapa en los tres tamaños, conservando ciudad, local, pabellón y piso. La navegación y los datos utilizados en estas capturas son de prueba; la revisión visual no sustituye una comprobación final con una sesión real.
