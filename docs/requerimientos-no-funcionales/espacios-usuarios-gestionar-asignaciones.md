# RNF-ESPACIOS-USUARIOS-001: Integridad y trazabilidad de asignaciones

| Campo | Valor |
|-------|-------|
| Módulo | EspaciosUsuarios |
| Categoría | Seguridad / Mantenibilidad |
| Fecha | 2026-08-01 |
| Autor | Leonardo Jaren |
| Estado | En revisión |

## Descripción

Las asignaciones deben preservar integridad referencial, evitar duplicados y registrar quién realizó cada cambio.

## Justificación

La relación define responsables operativos de ambientes institucionales. Datos duplicados o eliminaciones físicas degradarían la trazabilidad de incidencias y activos.

## Métrica / umbral

| Métrica | Valor objetivo |
|---------|----------------|
| Pares usuario–espacio duplicados | 0 |
| Escrituras realizadas por técnicos | 0 permitidas |
| Asignaciones sin usuario o espacio válido | 0 |
| Consultas de listado | Relaciones precargadas para evitar consultas repetitivas |
| Opciones cargadas por solicitud en selectores grandes | Máximo 10 registros |

## Implementación esperada

- Restricción única de base de datos sobre usuario y espacio.
- Auditoría heredada desde `shared.models.BaseModel`.
- `select_related` aplicado desde el repository.
- Borrado lógico para conservar trazabilidad.
- Validación en service y permisos en ViewSet.
- Selector paginado reutilizable con búsqueda remota para no descargar catálogos completos.

## Verificación

- [x] Ejecutar `python manage.py test espacios`.
- [x] Ejecutar las pruebas Vitest de `useEspaciosUsuarios`.
- [x] Ejecutar las pruebas Vitest de `BasePaginatedSelect`.
- [x] Verificar migraciones con `makemigrations espacios --check --dry-run`.

## Relación con RF

- RF relacionados: RF-ESPACIOS-USUARIOS-001

## Notas

Las clases reutilizan `BaseRepository`, `BaseService`, `BaseViewSet` y `BaseModel` del paquete `shared`.
