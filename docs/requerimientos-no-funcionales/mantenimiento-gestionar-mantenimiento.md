# RNF-MANT-001: Calidad y seguridad de la gestión de mantenimiento

## Arquitectura

- Las vistas (`MantenimientoViewSet`, `EquipoViewSet`) delegan reglas de
  negocio a sus servicios respectivos.
- El acceso ORM se concentra en `MantenimientoRepository` y
  `EquipoRepository`.
- Los modelos reutilizan `BaseModel` para auditoría y borrado lógico.
- Los serializers de lectura y escritura tienen responsabilidades separadas
  (`MantenimientoSerializer` vs `MantenimientoCreateUpdateSerializer`).

## Seguridad

- Todos los endpoints requieren autenticación JWT.
- Administradores tienen acceso total (CRUD) al módulo.
- Técnicos pueden listar, crear y actualizar tickets, pero no eliminarlos.
- Usuarios sin rol administrativo o técnico no pueden acceder al módulo.

## Experiencia de usuario

- La interfaz reutiliza los componentes base existentes (`BaseTable`,
  `BaseModal`, `BaseSelect`, `StatCard`, `BasePagination`) y la paleta
  centralizada en `style.css`.
- Los estados de carga, vacío, éxito y error son visibles mediante
  `BaseToast` y los estados de `BaseTable`.
- Los badges de estado usan colores consistentes con el resto de la app
  (éxito, primario, peligro, neutro).

## Pruebas

- El backend se validó de extremo a extremo (login, listar, crear, editar,
  eliminar, estadísticas y opciones) contra la base de datos real.
- El frontend se validó con `npm run build` y la suite existente
  (`npm run test`) sin regresiones.

## Relación con RF

- RF relacionados: RF-MANT-001
