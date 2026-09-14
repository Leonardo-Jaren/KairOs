# RNF-ESP-004: Rendimiento, Integridad y Usabilidad del Mapa por Locales

| Campo | Valor |
|-------|-------|
| Módulo | Espacios y Campus Tecnológico |
| Categoría | Rendimiento / Integridad Referencial / Usabilidad |
| Fecha | 2026-09-14 |
| Autor | Equipo KairOs |
| Estado | Aprobado |

## Descripción

El módulo de navegación territorial y mapa de infraestructura (`/espacios/mapa`) permite explorar los edificios, pisos y ambientes organizados jerárquicamente por ciudad y local. Este flujo debe garantizar una experiencia interactiva sin latencia perceptible, una rigurosa integridad de datos en operaciones de borrado y desactivación, y un aislamiento total entre contextos territoriales.

## Justificación

La supervisión de múltiples sedes físicas (locales) y campus tecnológicos requiere que los operadores técnicos y administradores conmuten entre diferentes ciudades y locales de manera instantánea, sin arrastrar estados residuales de sedes previas y asegurando que ninguna sede con infraestructura física asignada quede huérfana o sea eliminada por error.

## Métricas y Umbrales de Rendimiento

| Métrica | Valor objetivo |
|---------|----------------|
| Tiempo de conmutación de local (`selectLocal`) | < 200 ms en renderizado de pabellones |
| Carga inicial de datos territoriales (`/api/v1/espacios/locales/`) | < 350 ms para catálogos de hasta 100 locales |
| Cálculo de estadísticas agregadas por sede | < 300 ms en llamada `/api/v1/espacios/edificios/estadisticas/` |
| Paginación exhaustiva en carga | 100% de páginas resueltas antes de calcular métricas de tarjetas |
| Tiempo de respuesta en creación/edición de local | < 400 ms en HTTP POST/PATCH |

## Requisitos de Integridad y Reglas de Negocio

1. **Bloqueo estricto de eliminación física y lógica:**
   - No se permite eliminar (`DELETE`) ni desactivar (`PATCH activo=false`) ningún local que conserve edificios o pabellones no eliminados (`is_deleted=False`), incluso si dichos edificios se encuentran marcados como inactivos.
   - El sistema debe responder con error semántico `400 Bad Request` indicando la imposibilidad de retirar el local mientras existan edificios vinculados.
2. **Aislamiento contextual de estado reactivo:**
   - Al cambiar de local o ciudad en el frontend, el pabellón seleccionado debe resetearse inmediatamente si no pertenece a la nueva sede.
   - Si el nuevo local no posee pabellones registrados, el croquis y los pisos deben limpiarse inmediatamente mostrando un estado vacío informativo con llamada a la acción.
3. **Zona de compatibilidad para registros legados:**
   - Los edificios registrados con anterioridad a la incorporación de la entidad `Local` deben agruparse bajo el selector especial `"Sin local asignado"` (`__legacy__`), permitiendo su consulta y posterior reasignación formal a una sede activa.
4. **Protección de ediciones en curso:**
   - Si el usuario se encuentra editando la distribución de un croquis de piso (`editingFloor=true`), los selectores de ciudad, local y botón de creación deben deshabilitarse o requerir confirmación explícita para evitar pérdida involuntaria de borradores.

## Verificación Automatizada

- **Backend (Django Tests):**
  - `backend/espacios/test_locales.py`: Valida CRUD, validaciones de código duplicado, restricción de borrado protegido con edificios vinculados y filtros por ciudad.
- **Frontend (Vitest Specs):**
  - `frontend/src/composables/espacios/useCampusTerritorio.spec.js`: Valida selección de ciudades, locales, filtros dinámicos, creación/edición/eliminación reactiva y manejo de errores de API.
  - `frontend/src/composables/espacios/useCampusTecnologico.spec.js`: Valida indicadores, cambio de pabellones, croquis y persistencia de distribución.

## Relación con Requerimientos e Historias de Usuario

- **Requerimiento Funcional:** [RF-ESP-004: Recorrer el mapa tecnológico por lugares](../requerimientos-funcionales/espacios-mapa-por-locales.md)
- **Historia de Usuario:** [HU-ESP-004: Navegación territorial y mapa de infraestructura](../historias-de-usuario/espacios-mapa-por-locales.md)
- **Diccionario de Datos:** Tabla `locales` y clave foránea `edificios.local_id` en [diccionario_de_datos.md](../base-de-datos/diccionario_de_datos.md).
