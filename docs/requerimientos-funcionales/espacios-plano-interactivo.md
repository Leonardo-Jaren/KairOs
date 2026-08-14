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
2. Selecciona un edificio y revisa el croquis de cada piso con sus laboratorios, aulas, oficinas y pasillos.
3. Si es administrador, diseña el piso: mueve ambientes, ajusta su tamaño y dibuja recorridos transitables.
4. Abre un ambiente y selecciona una estación para consultar su ficha, componentes, software y mantenimientos activos.
5. Si es administrador, activa el modo edición, ajusta filas o columnas y reubica los equipos.
6. Guarda la distribución para que esté disponible a los demás usuarios.
7. Desde el plano puede crear, editar o retirar una PC y completar su hardware o software.
8. Desde la ficha de una estación, registra una falla indicando el usuario reportante o la envía inmediatamente a mantenimiento.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Espacio sin equipos | Se muestra un estado vacío con la acción para crear la primera PC allí mismo. |
| Equipo de otro espacio en el plano | La API rechaza la configuración y conserva la distribución anterior. |
| Posiciones repetidas o fuera del plano | La API responde con error de validación. |
| Técnico intenta editar la distribución | Mantiene acceso de lectura, pero no se muestra el modo edición. |
| Ambientes superpuestos en el croquis | La API rechaza la distribución del piso y conserva la anterior. |
| Pasillo sobre un ambiente | La interfaz evita la acción y la API valida nuevamente antes de guardar. |
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
- Cada ambiente activo debe aparecer una sola vez en el croquis de su piso.
- Los ambientes pueden ocupar varias celdas para representar laboratorios de mayor tamaño.
- Un pasillo no puede ocupar una celda cubierta por un aula, laboratorio u oficina.
- El croquis del piso admite entre 6 y 16 columnas y entre 3 y 12 filas.

## Criterios de aceptacion

- [x] Los pabellones históricos se migran a edificios administrables.
- [x] Cada edificio muestra sus ambientes agrupados por piso y se adapta a seis o más tarjetas.
- [x] Cada piso se representa como un croquis con ambientes de distinto tamaño y pasillos editables.
- [x] El administrador puede mover y redimensionar ambientes, dibujar pasillos y persistir la planta.
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
| API | `PATCH /api/v1/espacios/edificios/{id}/croquis-piso/` |
| API | `GET /api/v1/espacios/{id}/` |
| API | `PATCH /api/v1/espacios/{id}/disposicion/` |
| API | `POST /api/v1/mantenimiento/` |
| Backend | `backend/espacios/` y `backend/mantenimiento/` |
| Frontend | `frontend/src/views/espacios/CampusTecnologicoView.vue` |
| Frontend | `frontend/src/components/espacios/CroquisPiso.vue` |
| Frontend | `frontend/src/views/espacios/EspacioDetalleView.vue` |

## Notas

La representación del campus utiliza cuadrículas derivadas de los datos existentes; no depende de una imagen fija ni de coordenadas geográficas. Cada piso genera inicialmente ambientes a ambos lados de un pasillo y dimensiona los bloques según el tipo y la cantidad de equipos. El croquis se guarda en el edificio, mientras que el plano de PCs continúa almacenándose dentro del espacio. La distribución automática de equipos reserva inicialmente un pasillo central cuando hay seis o más columnas. Después, cualquier columna interna completamente vacía se representa como pasillo para que el plano responda a la distribución real guardada.
