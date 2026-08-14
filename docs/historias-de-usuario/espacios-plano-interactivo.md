# HU-ESPACIOS-02: Gestionar laboratorios desde un plano interactivo

| Campo | Valor |
|-------|-------|
| Modulo | Espacios |
| Prioridad | Alta |
| Fecha | 2026-08-14 |
| Autor | Leonardo Jaren |
| Estado | Hecho |

## Historia

**Como** administrador o técnico de soporte

**Quiero** recorrer los edificios y operar sobre las estaciones de cada laboratorio desde un plano visual

**Para** localizar rápidamente los equipos, entender su estado y atender fallas sin buscar manualmente en varias tablas.

## Descripcion

El mapa tecnológico complementa el inventario tradicional con una vista espacial. La distribución de cada laboratorio puede adaptarse a diferentes cantidades de equipos, filas, columnas y pasillos, manteniendo las acciones operativas conectadas con Equipos y Mantenimiento.

## Criterios de aceptacion

- [x] **Dado** que existen espacios activos, **cuando** se abre el mapa, **entonces** se muestran agrupados por edificio con sus laboratorios y métricas.
- [x] **Dado** un laboratorio con equipos, **cuando** se abre su plano, **entonces** cada estación presenta un color según su estado.
- [x] **Dado** un administrador en modo edición, **cuando** mueve una estación y guarda, **entonces** la nueva posición persiste en la base de datos.
- [x] **Dado** un equipo seleccionado, **cuando** se abre su ficha, **entonces** se muestran sus características principales.
- [x] **Dado** un equipo con una falla, **cuando** se envía a mantenimiento, **entonces** se crea un ticket correctivo y el equipo cambia a En mantenimiento.

## Alcance tecnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `PATCH /api/v1/espacios/{id}/disposicion/` y `POST /api/v1/mantenimiento/` |
| Service | `backend/espacios/services/espacio_service.py` y `backend/mantenimiento/services/mantenimiento_service.py` |
| Repository | `backend/espacios/repositories/` y `backend/mantenimiento/repositories/` |
| Frontend | `frontend/src/composables/espacios/useCampusTecnologico.js` y `usePlanoEspacio.js` |

## RF / RNF relacionados

- RF: `RF-ESPACIOS-02`
- RNF: N/A

## Notas de implementacion

La configuración del plano se almacena como JSON validado dentro del espacio. La interfaz genera una distribución inicial automática para equipos que todavía no tienen posición guardada.

## Enlaces

- PR: N/A
- Issue GitHub: N/A
