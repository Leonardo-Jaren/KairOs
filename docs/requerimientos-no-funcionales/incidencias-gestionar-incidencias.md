# RNF-INCI-001: Calidad y seguridad de la gestión de incidencias

## Arquitectura

- El flujo respeta `ViewSet -> Serializer -> Service -> Repository -> Model`.
- `IncidenciaService` concentra transiciones, alcance territorial, validación
  equipo-espacio y relación con mantenimientos.
- `IncidenciaRepository` concentra consultas y precarga relaciones para evitar
  consultas N+1 en la cola y el detalle.
- `BaseModel` mantiene auditoría y borrado lógico; nunca se eliminan registros
  históricos físicamente desde la operación normal.

## Seguridad y alcance

- Todos los endpoints requieren autenticación JWT y permisos del módulo.
- `docente` y `usuario` solo pueden consultar sus propias incidencias y crear
  reportes; no pueden editar, eliminar ni cambiar estados.
- `tecnico`, `responsable`, `admin` y `superadmin` operan únicamente espacios
  autorizados. La autorización por objeto se valida en backend, aunque el
  frontend oculte acciones.
- Una incidencia no acepta un equipo que no pertenezca al espacio enviado.
- Incidencias `cerrado`, `cancelado` o `duplicado` son inmutables.

## Rendimiento y experiencia

- La cola admite filtros por prioridad, estado, espacio, equipo, técnico y
  antigüedad, con consultas paginables.
- La interfaz muestra prioridad, equipo, espacio, reportante, técnico, órdenes
  asociadas y resolución en un detalle con línea de tiempo y progreso del caso.
- Las acciones operativas se presentan como botones contextuales (`Atender
  incidencia`, `Crear correctivo`, `Crear otra intervención`, `Cerrar
  incidencia` y `Ver mantenimiento`); finalizar un correctivo funcional cierra
  la incidencia de forma transaccional y comunica el resultado.
- El formulario dependiente carga equipos después del espacio y nunca permite
  elegir combinaciones inválidas.

## Pruebas obligatorias

Se deben cubrir autorización por rol y espacio, creación siempre pendiente,
transiciones válidas e inválidas, resolución/cierre, cierre automático por
correctivo funcional, permanencia abierta ante equipo dañado, motivos de
cancelación y duplicidad, consistencia equipo-espacio, creación de correctivo y
preservación del espacio histórico tras un traslado.
