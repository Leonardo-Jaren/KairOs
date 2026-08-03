# RNF-EQUI-001: Calidad y seguridad de la gestión de equipos

## Arquitectura

- `EquipoViewSet` delega las reglas de negocio a `EquipoService`.
- El acceso ORM se concentra en `EquipoRepository`, que precarga la relación
  con `Espacio` para evitar consultas N+1.
- El modelo `Equipo` reutiliza `BaseModel` para auditoría y borrado lógico.
- Los serializers de lectura y escritura tienen responsabilidades separadas
  (`EquipoSerializer` vs `EquipoCreateUpdateSerializer`).

## Seguridad

- Todos los endpoints requieren autenticación JWT.
- Administradores tienen acceso total (CRUD) al módulo (`CanManageEquipo`).
- Técnicos solo pueden consultar (métodos seguros); cualquier intento de
  escritura se rechaza con 403.
- Usuarios sin rol administrativo o técnico no pueden acceder al módulo.

## Experiencia de usuario

- La interfaz reutiliza los componentes base existentes (`BaseTable`,
  `BaseModal`, `BaseSelect`, `StatCard`, `BasePagination`) y la paleta
  centralizada en `style.css`.
- Los estados de carga, vacío, éxito y error son visibles mediante
  `BaseToast` y los estados de `BaseTable`.
- Los badges de estado y tipo usan colores consistentes con el resto de la
  app (éxito, advertencia, peligro, neutro).
- Los técnicos ven las acciones de edición y retiro ocultas, mostrando en su
  lugar la indicación "Solo lectura".

## Pruebas

- El backend se validó de extremo a extremo (login, listar, crear, editar,
  eliminar y estadísticas) contra la base de datos real.
- El frontend se validó con `npm run build` y la suite existente
  (`npm run test`) sin regresiones.

## Relación con RF

- RF relacionados: RF-EQUI-001
