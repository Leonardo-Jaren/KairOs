# RNF-EQ-002: Integridad y Trazabilidad de Componentes de Hardware

| Campo | Valor |
|-------|-------|
| Modulo | Equipos y Componentes |
| Categoria | Mantenibilidad / Integridad |
| Fecha | 2026-09-14 |
| Autor | Equipo KairOs |
| Estado | Aprobado |

## Descripcion

El subsistema de inventario de hardware debe asegurar la integridad referencial y el seguimiento histórico de cada componente interno (CPU, RAM, almacenamiento, GPU, fuente de poder) asociado a los equipos informáticos, garantizando que ninguna baja o transferencia genere inconsistencias patrimoniales.

## Justificacion

El control patrimonial de hardware institucional exige trazabilidad exacta de seriales, marcas y capacidades técnicas para prevenir pérdidas o discrepancias durante auditorías de inventario.

## Metrica / umbral

| Metrica | Valor objetivo |
|---------|----------------|
| Tiempo de consulta de componentes por equipo | < 200 ms |
| Integridad referencial | 100% mediante FK con borrado lógico o CASCADE controlado |
| Validación de unicidad de serial | Inmediata a nivel de base de datos y serializador |

## Implementacion esperada

- Modelo `Componente` enlazado mediante clave foránea a `Equipo`.
- Borrado lógico (`is_deleted`) para conservar historial de componentes retirados.
- Validación de parámetros y tipos permitidos mediante choices normalizados en Django ORM.

## Verificacion

- [x] Pruebas unitarias de repositorios y modelos de componentes en `backend/equipos/`.
- [x] Pruebas unitarias del composable `useComponentes.spec.js` en Vitest.

## Relacion con RF

- RF relacionados: RF-EQ-002 (Gestión de componentes de hardware).

## Notas

Permite vincular componentes a tickets de reemplazo en el módulo de mantenimiento.
