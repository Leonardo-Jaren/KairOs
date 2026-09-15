# RNF-HIST-001: Inmutabilidad, Rendimiento y Disponibilidad del Log de Auditoría

| Campo | Valor |
|-------|-------|
| Modulo | Historial y Auditoría |
| Categoria | Seguridad / Rendimiento |
| Fecha | 2026-09-14 |
| Autor | Equipo KairOs |
| Estado | Aprobado |

## Descripcion

El log de auditoría debe ser rigurosamente inmutable a través de cualquier punto de acceso externo (API REST), garantizando que los registros no puedan ser adulterados, modificados ni suprimidos una vez persistidos en la base de datos. Asimismo, las consultas sobre volúmenes crecientes de eventos deben mantenerse por debajo de los umbrales de latencia establecidos.

## Justificacion

Para auditorías institucionales y peritaje de incidentes informáticos, es mandatorio contar con registros de eventos íntegros e inalterables con marcas de tiempo confiables.

## Metrica / umbral

| Metrica | Valor objetivo |
|---------|----------------|
| Tiempo de inserción de evento de auditoría | < 50 ms (sin bloquear la transacción principal) |
| Latencia de consulta paginada (20 eventos) | < 300 ms |
| Inmutabilidad vía API REST | 100% (código HTTP 405 en POST, PUT, PATCH, DELETE) |
| Integridad cronológica | Ordenamiento estricto por `fecha DESC` mediante índice B-Tree |

## Implementacion esperada

- Tabla `historial` indexada por `fecha`, `usuario` y `tipo_evento`.
- Uso de `GenericForeignKey` de `django.contrib.contenttypes` para enlazar modelos heterogéneos sin bloquear esquemas.
- ViewSet `HistorialViewSet` configurado como `ReadOnlyModelViewSet` o bloqueando métodos mutadores.

## Verificacion

- [x] Pruebas unitarias en `backend/historial/tests.py` validando el rechazo de HTTP 405 en llamadas no autorizadas.
- [x] Verificación de índices de base de datos (`idx_historial_fecha`, `idx_historial_tipo`).

## Relacion con RF

- RF relacionados: RF-HIST-001 (Registro y consulta de auditoría).

## Notas

La generación de eventos se orquesta a través del servicio centralizado de historial en backend.
