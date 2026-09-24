# RF-INCI-001: Registrar y gestionar incidencias de equipos

## Descripción

Una incidencia representa una falla o degradación no planificada que afecta o
puede afectar la disponibilidad de un equipo de cómputo. Es distinta de una
orden de mantenimiento: un reporte puede resolverse sin mantenimiento y una
orden correctiva puede originarse desde la incidencia.

## Criterios funcionales

- `docente` y `usuario` pueden crear incidencias y consultar únicamente las
  incidencias que reportaron.
- `tecnico`, `responsable`, `admin` y `superadmin` pueden realizar triage,
  asignar técnicos, cambiar prioridad y estado, registrar resolución y crear
  mantenimientos correctivos dentro de sus espacios autorizados.
- Toda incidencia se asocia obligatoriamente a un equipo vigente, un espacio y
  un tipo (`hardware` o `software`). El backend valida que equipo y espacio
  coincidan.
- Una incidencia nueva siempre inicia en `pendiente`; el cliente no puede
  crearla directamente como resuelta.
- Los estados son `pendiente`, `en_proceso`, `resuelto`, `cerrado`, `cancelado`
  y `duplicado`.
- Las transiciones válidas son:

  ```text
  pendiente -> en_proceso | cancelado | duplicado
  en_proceso -> resuelto | cancelado | duplicado
  resuelto -> cerrado | en_proceso
  ```

- Resolver exige `resolucion` y registra `fecha_resolucion` con fecha y hora.
  Volver a `en_proceso` limpia la fecha. Cerrar conserva una resolución y una
  incidencia terminal no se edita.
- Cancelar o marcar como duplicada exige `motivo_cierre`.
- Se registra `prioridad` (`baja`, `media`, `alta`, `critica`) y un técnico
  opcional en `asignado_a`.
- El borrado es lógico y no elimina el historial.
- La incidencia conserva el espacio donde fue reportada aunque el equipo se
  traslade después.
- Una incidencia puede tener cero, uno o varios mantenimientos relacionados.

## Flujo operativo

```text
Reporte -> pendiente -> triage -> en_proceso
    |                         |        |
    +-> cancelada/duplicada   |        +-> resuelto -> cerrado
                              +-> resolución remota
                              +-> correctivo relacionado
```

Un mantenimiento correctivo no cierra la incidencia inmediatamente. La
 persona operativa inicia y finaliza la orden con una prueba. Si el equipo queda
 funcional, el sistema registra el trabajo como resolución y cierra la
 incidencia automáticamente; si queda dañado, la incidencia permanece abierta.

## Endpoints

| Método | Endpoint | Uso |
|---|---|---|
| `GET` | `/api/v1/incidencias/` | Cola filtrable por espacio, equipo, estado, tipo y texto; el resultado respeta el alcance del usuario. |
| `POST` | `/api/v1/incidencias/` | Crear reporte; siempre queda `pendiente`. |
| `GET` | `/api/v1/incidencias/{id}/` | Detalle de la incidencia visible para el actor. |
| `PATCH` | `/api/v1/incidencias/{id}/` | Triage, prioridad, asignación y transición operativa. |
| `GET` | `/api/v1/incidencias/{id}/mantenimientos/` | Órdenes relacionadas. |
| `POST` | `/api/v1/incidencias/{id}/crear-mantenimiento/` | Crear correctivo con el mismo equipo. |
| `GET` | `/api/v1/incidencias/estadisticas/` | Indicadores de la cola según alcance. |

## Capas relacionadas

`IncidenciaViewSet -> IncidenciaSerializer -> IncidenciaService ->
IncidenciaRepository -> Incidencia`.

Las incidencias generales de red, energía, mobiliario, capacitación o tareas
administrativas quedan fuera de este alcance inicial.
