# RNF-INCI-001: Calidad y seguridad de la gestion de incidencias

## Arquitectura

- `IncidenciaViewSet` delega las reglas de negocio a
  `IncidenciaService`.
- El acceso ORM se concentra en `IncidenciaRepository`, que precarga
  `espacio`, `equipo` y `created_by` (`select_related`) para evitar
  consultas N+1 en el listado.
- El modelo `Incidencia` reutiliza `BaseModel` para auditoria y
  borrado logico; `created_by` cubre "quien registro la incidencia"
  sin necesidad de campos custom por rol.

## Seguridad

- Todos los endpoints requieren autenticacion JWT.
- Administradores y tecnicos tienen acceso total (crear, editar,
  cambiar estado, eliminar).
- Docentes solo pueden crear (reportar); no pueden editar ni eliminar
  incidencias existentes, ni las propias.
- Usuarios sin rol administrativo, tecnico o docente no pueden
  acceder al modulo.

## Experiencia de usuario

- La interfaz reutiliza los componentes base existentes (`BaseTable`,
  `BaseModal`, `BaseSelect`, `StatCard`, `BasePagination`).
- Los badges de estado usan los mismos colores semanticos que
  Mantenimiento (pendiente / en proceso / resuelto) para mantener
  consistencia visual entre modulos.

## Pruebas

- El backend se valida de extremo a extremo (listar, crear, cambiar
  estado, eliminar, filtros) contra la base de datos real.
- El frontend se valida con `npm run build` y navegacion real en
  navegador antes de reportar el modulo como completo.

## Relacion con RF

- RF relacionados: RF-INCI-001
