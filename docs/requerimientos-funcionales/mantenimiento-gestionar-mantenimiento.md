# RF-MANT-001: Gestionar mantenimiento de equipos

## Descripción

El sistema debe permitir registrar, consultar, editar y eliminar tickets de
mantenimiento preventivo y correctivo de los equipos, asignando un técnico
responsable y llevando seguimiento de su estado.

## Criterios funcionales

- Administradores y técnicos pueden crear y editar tickets de mantenimiento.
- Solo administradores pueden eliminar tickets (borrado lógico).
- Cada ticket se asocia a un equipo vigente y, opcionalmente, a uno o más
  técnicos mediante la relación existente `TecnicoMantenimiento`.
- Cada ticket conserva el usuario que reportó la falla. Al crear desde el plano
  se usa por defecto el usuario autenticado, con opción de seleccionar otro
  usuario activo.
- El listado permite filtrar por texto (equipo, descripción, técnico), tipo
  de mantenimiento y estado, con paginación.
- El estado del ticket se presenta como Pendiente, En mantenimiento,
  Terminado o Fuera de servicio.
- El módulo expone indicadores agregados: técnicos registrados, dispositivos,
  tickets en curso y pendientes.
- Se exponen endpoints de apoyo (`/opciones/`, `/tecnicos-disponibles/`) para
  poblar los selectores de equipo y técnico responsable en el formulario.
- El módulo de equipos (`backend/equipos/`) se implementó como soporte de
  esta historia, ya que el ticket de mantenimiento depende de un equipo
  vigente.
