# RNF-SOFT-001: Calidad y seguridad de la gestión de software

## Arquitectura

- `ProductoSoftwareViewSet` y `SoftwareInstaladoViewSet` delegan las reglas de
  negocio a `ProductoSoftwareService` y `SoftwareInstaladoService`
  respectivamente.
- El acceso ORM se concentra en `ProductoSoftwareRepository` y
  `SoftwareInstaladoRepository`, que precargan `equipo` y `producto_software`
  (`select_related`) para evitar consultas N+1 en los listados.
- Ambos modelos reutilizan `BaseModel` para auditoría y borrado lógico.
- Los serializers de lectura y escritura tienen responsabilidades separadas
  (`ProductoSoftwareSerializer` vs `ProductoSoftwareCreateUpdateSerializer`,
  y su equivalente para instalaciones).
- Se ajusta la propiedad `ProductoSoftware.licencias_disponibles` para
  contar solo instalaciones vigentes (`is_deleted=False`).

## Seguridad

- Todos los endpoints requieren autenticación JWT.
- Administradores y técnicos tienen acceso total (CRUD) al módulo
  (`CanManageSoftware`).
- Docentes solo pueden consultar (métodos seguros); cualquier intento de
  escritura se rechaza con 403.
- Usuarios sin rol administrativo, técnico o docente no pueden acceder al
  módulo.

## Experiencia de usuario

- La interfaz reutiliza los componentes base existentes (`BaseTable`,
  `BaseModal`, `BaseSelect`, `StatCard`, `BasePagination`) y la paleta
  centralizada en `style.css`.
- Los indicadores de licencias próximas a expirar y sobre-utilizadas se
  muestran con badges de advertencia/peligro consistentes con el resto de la
  app.
- Los docentes ven las acciones de creación, edición y eliminación ocultas,
  mostrando en su lugar la indicación "Solo lectura".

## Pruebas

- El backend se valida de extremo a extremo (listar, crear, editar, eliminar,
  filtros por espacio/equipo/producto y estadísticas) contra la base de datos
  real.
- El frontend se valida con `npm run build` y la suite existente
  (`npm run test`) sin regresiones.

## Relación con RF

- RF relacionados: RF-SOFT-001, RF-SOFT-002
