# HU-INCI-001: Reportar y atender una falla de equipo

Como docente o usuario quiero reportar una falla de una computadora y consultar
su estado, para que el personal técnico la atienda sin perder el historial.

Como técnico o responsable quiero clasificar el reporte, asignar trabajo y
relacionar mantenimientos correctivos, para resolver y cerrar la incidencia con
trazabilidad.

## Criterios de aceptación

1. El reportante selecciona un espacio y, después, un equipo perteneciente a
   ese espacio; la incidencia se crea en `pendiente`.
2. Docentes y usuarios ven solo sus propios reportes y no pueden editar,
   borrar ni cambiar estados después del envío.
3. El personal operativo ve la cola de sus espacios autorizados con prioridad,
   antigüedad, equipo, espacio, reportante y técnico asignado.
4. El triage permite pasar a `en_proceso`, cancelar o marcar duplicada con
   motivo; resolver exige una explicación.
5. Una incidencia resuelta puede cerrarse después de verificar el equipo o
   volver a `en_proceso` si reaparece la falla.
6. Un técnico puede crear uno o varios mantenimientos correctivos relacionados;
   el equipo debe coincidir. La orden se inicia y finaliza con acciones guiadas,
   no con el lápiz de edición.
7. Al finalizar un correctivo vinculado, con prueba confirmada y resultado
   `en_uso`, el sistema copia el trabajo realizado como resolución y cierra la
   incidencia automáticamente. Si el resultado es `dañado` o `de_baja`, la
   incidencia permanece en atención y ofrece crear otra intervención.
8. Un mantenimiento preventivo puede finalizar sin incidencia y no modifica
   ningún reporte; una avería encontrada durante el preventivo se reporta como
   una nueva incidencia.
9. El detalle muestra línea de progreso, resolución, órdenes asociadas y la
   siguiente acción recomendada.
10. La ficha del equipo muestra su estado actual, incidencias abiertas,
    mantenimientos en curso e historial de intervenciones.

## Alcance técnico

| Capa | Archivos / endpoints |
|---|---|
| API | `GET/POST /api/v1/incidencias/`, `PATCH /api/v1/incidencias/{id}/`, `GET /api/v1/incidencias/{id}/mantenimientos/`, `POST /api/v1/incidencias/{id}/crear-mantenimiento/`, `POST /api/v1/mantenimiento/{id}/iniciar/`, `POST /api/v1/mantenimiento/{id}/finalizar/` |
| Service | `backend/incidencias/services/incidencia_service.py` |
| Repository | `backend/incidencias/repositories/incidencia_repository.py` |
| UI | `frontend/src/views/incidencias/IncidenciasView.vue` y ficha del equipo |
| Auditoría | `backend/shared/mixins/audit.py` |

## RF / RNF relacionados

- RF: `docs/requerimientos-funcionales/incidencias-gestionar-incidencias.md`
- RNF: `docs/requerimientos-no-funcionales/incidencias-gestionar-incidencias.md`
