# HU-EQUI-001: Gestionar inventario de equipos

Como administrador de KairOs, quiero registrar y mantener actualizado el
inventario de equipos informáticos para conocer su ubicación, estado y datos
técnicos en todo momento.

## Criterios de aceptación

1. Puedo listar equipos con búsqueda, filtros e indicadores (total, en uso,
   en mantenimiento, de baja).
2. Puedo registrar un equipo indicando código, número de serie, tipo, marca,
   modelo, modo de adquisición, fecha de adquisición, estado y espacio
   asignado.
3. Puedo editar un equipo existente, incluyendo su estado y espacio.
4. Puedo retirar un equipo conservando su historial de mantenimientos
   (borrado lógico).
5. Un técnico puede consultar el inventario, pero no crear, editar ni
   retirar equipos.
6. Un usuario sin rol administrativo o técnico no puede acceder al módulo.
7. Los estados se presentan como En uso, En mantenimiento, Dañado y De baja,
   con colores distintivos.
8. Cuento con un usuario administrador y datos de prueba (`crear_admin_prueba`
   y `seed_datos_prueba`) para validar el módulo localmente.

## Enlaces

- PR: https://github.com/Leonardo-Jaren/KairOs/pull/9
- Issue GitHub: https://github.com/Leonardo-Jaren/KairOs/issues/10
