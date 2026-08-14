# RF-ESPACIOS-02: Explorar y editar el plano tecnológico del campus

| Campo | Valor |
|-------|-------|
| Modulo | Espacios |
| Version | 1.0 |
| Fecha | 2026-08-14 |
| Autor | Leonardo Jaren |
| Estado | En revisión |

## Descripcion

El sistema debe ofrecer una navegación visual por edificios, pisos y ambientes, además de un plano editable que represente la ubicación real de los equipos de cada laboratorio o aula tecnológica.

## Actores

- Administrador
- Técnico

## Precondiciones

- El usuario inició sesión con rol administrador o técnico.
- Los espacios y equipos se encuentran registrados y relacionados en KairOs.

## Flujo principal

1. El usuario abre el mapa tecnológico desde el módulo Espacios.
2. Selecciona un edificio y revisa sus pisos, laboratorios, aulas, oficinas, equipos y alertas.
3. Abre un ambiente y selecciona una estación para consultar su ficha, componentes, software y mantenimientos activos.
4. Si es administrador, activa el modo edición, ajusta filas o columnas y reubica los equipos.
5. Guarda la distribución para que esté disponible a los demás usuarios.
6. Desde el plano puede crear, editar o retirar una PC y completar su hardware o software.
7. Desde la ficha de una estación, registra una falla indicando el usuario reportante o la envía inmediatamente a mantenimiento.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Espacio sin equipos | Se muestra un estado vacío con la acción para crear la primera PC allí mismo. |
| Equipo de otro espacio en el plano | La API rechaza la configuración y conserva la distribución anterior. |
| Posiciones repetidas o fuera del plano | La API responde con error de validación. |
| Técnico intenta editar la distribución | Mantiene acceso de lectura, pero no se muestra el modo edición. |
| Falla pendiente | Se crea el ticket correctivo sin alterar el estado actual del equipo. |
| Falla enviada a mantenimiento | Se crea el ticket en proceso y el equipo cambia a En mantenimiento. |

## Reglas de negocio

- Cada equipo puede ocupar un único puesto dentro del plano.
- Dos equipos no pueden compartir la misma fila y columna.
- Solo se pueden ubicar equipos asignados al espacio consultado.
- El plano admite entre 2 y 10 columnas y entre 1 y 20 filas.
- Solo un equipo puede marcarse como estación del docente.
- La distribución física solo puede ser modificada por administradores.
- Los administradores y técnicos pueden registrar tickets correctivos desde el plano.
- El usuario autenticado se propone como reportante de la falla y puede reemplazarse por otro usuario activo.
- Los edificios son entidades independientes; desactivarlos conserva sus espacios e historial.

## Criterios de aceptacion

- [x] Los pabellones históricos se migran a edificios administrables.
- [x] Cada edificio muestra sus ambientes agrupados por piso y se adapta a seis o más tarjetas.
- [x] El administrador puede crear, editar y desactivar edificios y ambientes desde Campus.
- [x] Cada ambiente presenta métricas operativas antes de abrir el plano.
- [x] Al seleccionar una estación se muestran código, marca, modelo, serie, MAC, responsable y fecha de adquisición.
- [x] Una estación con falla muestra el ticket activo, reportante y técnico responsable.
- [x] El administrador puede crear, editar o retirar PCs y gestionar componentes y software sin salir del flujo del plano.
- [x] El administrador puede reubicar estaciones y persistir la distribución.
- [x] El sistema impide guardar equipos ajenos, repetidos o fuera de la cuadrícula.
- [x] Registrar una falla permite dejarla pendiente o enviarla a mantenimiento.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET /api/v1/espacios/` |
| API | `GET, POST /api/v1/espacios/edificios/` |
| API | `PATCH, DELETE /api/v1/espacios/edificios/{id}/` |
| API | `GET /api/v1/espacios/{id}/` |
| API | `PATCH /api/v1/espacios/{id}/disposicion/` |
| API | `POST /api/v1/mantenimiento/` |
| Backend | `backend/espacios/` y `backend/mantenimiento/` |
| Frontend | `frontend/src/views/espacios/CampusTecnologicoView.vue` |
| Frontend | `frontend/src/views/espacios/EspacioDetalleView.vue` |

## Notas

La representación del campus utiliza una cuadrícula responsive derivada de los datos existentes; no depende de una imagen fija ni de coordenadas geográficas. La distribución automática de equipos reserva un pasillo central cuando hay seis o más columnas.
