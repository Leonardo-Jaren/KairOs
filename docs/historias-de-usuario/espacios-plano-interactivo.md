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

**Quiero** recorrer los edificios mediante croquis por piso y operar sobre las estaciones de cada laboratorio desde un plano visual

**Para** localizar rápidamente los equipos, entender su estado y atender fallas sin buscar manualmente en varias tablas.

## Descripcion

El mapa tecnológico complementa el inventario tradicional con dos escalas espaciales: el croquis del piso organiza aulas, laboratorios y pasillos; el plano interno distribuye las PCs del ambiente. Ambas escalas mantienen las acciones operativas conectadas con Equipos y Mantenimiento.

## Criterios de aceptacion

- [x] **Dado** que existen espacios activos, **cuando** se abre Campus, **entonces** se muestran agrupados por edificio y piso, incluyendo laboratorios, aulas y oficinas.
- [x] **Dado** un administrador, **cuando** gestiona Campus, **entonces** puede crear, editar o desactivar edificios y ambientes sin abandonar la vista.
- [x] **Dado** un piso con ambientes, **cuando** se abre Campus, **entonces** se muestra un croquis que diferencia aulas, laboratorios y pasillos.
- [x] **Dado** un administrador, **cuando** diseña un piso, **entonces** puede mover y redimensionar ambientes o dibujar pasillos sin superponerlos.
- [x] **Dado** un laboratorio con equipos, **cuando** se abre su plano, **entonces** cada estación presenta un color según su estado.
- [x] **Dado** un administrador en modo edición, **cuando** mueve una estación y guarda, **entonces** la nueva posición persiste en la base de datos.
- [x] **Dado** un equipo seleccionado, **cuando** se abre su ficha, **entonces** se muestran sus características principales.
- [x] **Dado** un administrador dentro del plano, **cuando** crea o edita una PC, **entonces** puede completar sus componentes y software desde la misma ficha.
- [x] **Dado** un equipo con atención activa, **cuando** se selecciona, **entonces** se visualiza qué falla tiene, quién la reportó y qué técnico está asignado.
- [x] **Dado** un equipo con una falla, **cuando** se envía a mantenimiento, **entonces** se crea un ticket correctivo y el equipo cambia a En mantenimiento.

## Alcance tecnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `PATCH /api/v1/espacios/edificios/{id}/croquis-piso/`, `PATCH /api/v1/espacios/{id}/disposicion/` y `POST /api/v1/mantenimiento/` |
| Service | `backend/espacios/services/edificio_service.py`, `espacio_service.py` y `backend/mantenimiento/services/mantenimiento_service.py` |
| Repository | `backend/espacios/repositories/` y `backend/mantenimiento/repositories/` |
| Frontend | `frontend/src/composables/espacios/useCampusTecnologico.js` y `usePlanoEspacio.js` |

## RF / RNF relacionados

- RF: `RF-ESPACIOS-02`
- RNF: N/A

## Notas de implementacion

El edificio almacena un JSON validado con el croquis independiente de cada piso. El espacio mantiene su propio JSON para el plano interno de equipos. La interfaz genera inicialmente bloques proporcionados a la cantidad de PCs, los distribuye alrededor de pasillos y mantiene fija la barra de guardado mientras se edita.

## Enlaces

- PR: N/A
- Issue GitHub: N/A
