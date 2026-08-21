# RF-SOFT-002: Gestionar instalaciones de software en equipos

## Descripción

El sistema debe permitir registrar, consultar, editar y eliminar las
instalaciones de un producto de software en un equipo específico, y consultar
el software instalado filtrando por espacio o por equipo, con alertas sobre
licencias próximas a expirar y licencias sobre-utilizadas.

## Criterios funcionales

- Solo administradores y técnicos pueden crear, editar y eliminar
  instalaciones. Los docentes solo pueden consultar.
- Cada instalación está asociada obligatoriamente a un equipo y a un producto
  de software existentes; ninguno de los dos puede cambiarse una vez creada
  la instalación (solo se editan número de licencia usado y fecha de
  instalación).
- No se puede duplicar la instalación del mismo producto en el mismo equipo
  (`uq_equipo_software`).
- No se puede registrar una instalación si el producto no tiene licencias
  disponibles (`licencias_usadas >= licencias_totales`); el sistema rechaza
  la operación con un error de validación.
- El listado admite filtros por espacio (`espacio_id`, vía el equipo
  asignado), por equipo (`equipo_id`) y por producto de software
  (`producto_software_id`), permitiendo ver el software instalado en cada
  equipo de cada espacio.
- El endpoint de estadísticas expone: total de instalaciones vigentes,
  cantidad de productos con licencias próximas a expirar (dentro de 30 días)
  y cantidad de productos con licencias sobre-utilizadas (instalaciones
  vigentes por encima de `licencias_totales`).
- La eliminación es un borrado lógico (`is_deleted=True`) y libera una
  licencia disponible del producto asociado.
- Cada alta, modificación y baja genera un evento de auditoría
  (`softwareinstalado.alta`, `softwareinstalado.actualizacion`,
  `softwareinstalado.baja`).

## Reglas de negocio

- Bloquear creación de instalación si `licencias_disponibles <= 0` en el
  producto de software seleccionado.
- El umbral de "próxima a expirar" es de 30 días desde la fecha actual sobre
  `fecha_expiracion`.
- Sobre-uso se define como instalaciones vigentes de un producto mayores a su
  `licencias_totales` (puede ocurrir si se reduce `licencias_totales`
  después de tener instalaciones activas).

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET /api/v1/software/instalaciones/` |
| API | `POST /api/v1/software/instalaciones/` |
| API | `PATCH /api/v1/software/instalaciones/{id}/` |
| API | `DELETE /api/v1/software/instalaciones/{id}/` |
| Backend | `backend/software/repositories/software_instalado_repository.py` |
| Backend | `backend/software/services/software_instalado_service.py` |
| Backend | `backend/software/serializers/software_instalado_serializers.py` |
| Backend | `backend/software/views/software_instalado_views.py` |

## Notas

Depende del catálogo definido en `RF-SOFT-001`.
