# RF-EQUI-001: Gestionar inventario de equipos

## Descripción

El sistema debe permitir registrar, consultar, editar y retirar equipos
informáticos del inventario, asociándolos a un espacio físico y controlando
su estado operativo.

## Criterios funcionales

- Solo administradores pueden crear, editar y retirar equipos.
- Los técnicos pueden consultar el listado de equipos, pero no modificarlos.
- Cada equipo puede asociarse opcionalmente a un espacio (`Espacio`); si no
  se asigna, el equipo queda marcado como "Sin asignar".
- El listado permite filtrar por texto (código, número de serie, marca o
  modelo), tipo de equipo y estado, con paginación.
- El tipo de equipo admite los valores Desktop, Laptop, Servidor, Impresora,
  Proyector, Monitor y Otro.
- El estado del equipo se presenta como En uso, En mantenimiento, Dañado o
  De baja.
- El modo de adquisición admite los valores Comprado, Arrendado y Donado.
- El módulo expone indicadores agregados: total de equipos, en uso, en
  mantenimiento y de baja.
- Se exponen endpoints de apoyo (`/opciones/`) para poblar los selectores de
  equipo en otros módulos (por ejemplo, mantenimiento).
- El retiro de un equipo es un borrado lógico que conserva su historial de
  mantenimientos asociados.
