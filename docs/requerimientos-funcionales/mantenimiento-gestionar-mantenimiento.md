# RF-MANT-001: Gestionar mantenimiento de equipos

## Descripción

Un mantenimiento es una orden de trabajo técnico sobre un equipo. Puede ser
preventivo, para reducir riesgos de falla, o correctivo, para atender una falla
existente. Es una entidad distinta de la incidencia que pudo originarlo.

## Criterios funcionales

- Un mantenimiento preventivo puede crearse sin incidencia.
- Un mantenimiento correctivo puede incluir `incidencia_origen`; la relación es
  opcional para conservar órdenes históricas y permitir correctivos creados
  directamente.
- Una incidencia puede tener más de un mantenimiento y el equipo debe ser el
  mismo. No se permite relacionar incidencias cerradas, canceladas o duplicadas.
- Los estados de la orden son `pendiente`, `en_proceso`, `resuelto` y
  `cancelado`; las transiciones válidas son:

  ```text
  pendiente -> en_proceso | cancelado
  en_proceso -> resuelto | cancelado
  ```

- Resolver exige `diagnostico`, `trabajo_realizado`, `prueba_realizada` y un
  resultado final (`en_uso`, `dañado` o `de_baja`); registra `fecha_fin`,
  `verificado_por` y `fecha_verificacion`. Al iniciar se registra
  `fecha_inicio`.
- `resultado_equipo` es independiente del estado de la orden. El resultado
  `en_mantenimiento` se conserva para registros históricos y no se ofrece como
  resultado final en la interfaz guiada.
- Una orden cancelada no marca automáticamente el equipo como fuera de
  servicio. Al terminar la última orden activa se sincroniza el estado del
  equipo con el resultado registrado.
- Un correctivo vinculado que termina con prueba confirmada y resultado `en_uso`
  cierra automáticamente la incidencia de origen. Si el resultado es `dañado`
  o `de_baja`, la orden termina pero la incidencia permanece abierta y sugiere
  crear otra intervención.
- El borrado es lógico; el historial conserva diagnóstico, trabajo y técnicos.

## Operación

1. El técnico abre una orden preventiva o crea un correctivo desde la cola de
   incidencias.
2. Asigna uno o más técnicos y pulsa `Iniciar atención` para pasar la orden a
   `en_proceso`.
3. Pulsa `Finalizar mantenimiento`, registra diagnóstico, trabajo, prueba y
   resultado del equipo.
4. Si queda funcional, el sistema actualiza el equipo y cierra la incidencia
   vinculada; si queda dañado, mantiene la incidencia abierta para otra orden.

## Endpoints

| Método | Endpoint | Uso |
|---|---|---|
| `GET` | `/api/v1/mantenimiento/` | Listado filtrable por equipo, tipo y estado, respetando alcance territorial. |
| `POST` | `/api/v1/mantenimiento/` | Crear preventivo o correctivo. |
| `GET` | `/api/v1/mantenimiento/{id}/` | Detalle, técnicos, incidencia de origen y resultado. |
| `PATCH` | `/api/v1/mantenimiento/{id}/` | Edición administrativa compatible; la finalización usa acciones específicas. |
| `POST` | `/api/v1/mantenimiento/{id}/iniciar/` | Inicia una orden pendiente. |
| `POST` | `/api/v1/mantenimiento/{id}/finalizar/` | Finaliza con diagnóstico, trabajo, prueba y resultado; puede cerrar la incidencia vinculada. |
| `GET` | `/api/v1/mantenimiento/tecnicos-disponibles/` | Técnicos vigentes para asignación. |
| `GET` | `/api/v1/mantenimiento/estadisticas/` | Indicadores del ámbito del actor. |

## Capas relacionadas

`MantenimientoViewSet -> MantenimientoSerializer -> MantenimientoService ->
MantenimientoRepository -> Mantenimiento`.
