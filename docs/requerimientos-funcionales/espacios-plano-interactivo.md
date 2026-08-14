# RF-ESPACIOS-02: Explorar y editar el plano tecnológico del campus

| Campo | Valor |
|-------|-------|
| Modulo | Espacios |
| Version | 1.0 |
| Fecha | 2026-08-14 |
| Autor | Leonardo Jaren |
| Estado | En revisión |

## Descripcion

El sistema debe ofrecer una navegación visual por edificios y laboratorios, además de un plano editable que represente la ubicación real de los equipos de cada ambiente.

## Actores

- Administrador
- Técnico

## Precondiciones

- El usuario inició sesión con rol administrador o técnico.
- Los espacios y equipos se encuentran registrados y relacionados en KairOs.

## Flujo principal

1. El usuario abre el mapa tecnológico desde el módulo Espacios.
2. Selecciona un edificio y revisa sus laboratorios, pisos, equipos y alertas.
3. Abre un laboratorio y selecciona una estación para consultar su ficha.
4. Si es administrador, activa el modo edición, ajusta filas o columnas y reubica los equipos.
5. Guarda la distribución para que esté disponible a los demás usuarios.
6. Desde la ficha de una estación, registra una falla pendiente o la envía inmediatamente a mantenimiento.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Espacio sin equipos | Se muestra un estado vacío con acceso al inventario de equipos. |
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

## Criterios de aceptacion

- [x] Los edificios se agrupan a partir del pabellón registrado.
- [x] Cada laboratorio presenta métricas operativas antes de abrir el plano.
- [x] Al seleccionar una estación se muestran código, marca, modelo, serie, MAC, responsable y fecha de adquisición.
- [x] El administrador puede reubicar estaciones y persistir la distribución.
- [x] El sistema impide guardar equipos ajenos, repetidos o fuera de la cuadrícula.
- [x] Registrar una falla permite dejarla pendiente o enviarla a mantenimiento.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET /api/v1/espacios/` |
| API | `GET /api/v1/espacios/{id}/` |
| API | `PATCH /api/v1/espacios/{id}/disposicion/` |
| API | `POST /api/v1/mantenimiento/` |
| Backend | `backend/espacios/` y `backend/mantenimiento/` |
| Frontend | `frontend/src/views/espacios/CampusTecnologicoView.vue` |
| Frontend | `frontend/src/views/espacios/EspacioDetalleView.vue` |

## Notas

La representación del campus utiliza bloques derivados de los datos existentes; no depende de una imagen fija ni de coordenadas geográficas.
