# RF-SOFT-001: Gestionar catálogo de productos de software

## Descripción

El sistema debe permitir registrar, consultar, editar y eliminar productos de
software (catálogo de licencias) con su versión, tipo de licencia, cantidad de
licencias totales, fecha de expiración y costo anual, sirviendo como base para
las instalaciones registradas en cada equipo.

## Criterios funcionales

- Solo administradores y técnicos pueden crear, editar y eliminar productos de
  software. Los docentes solo pueden consultar el catálogo.
- Un producto se identifica por la combinación única de nombre de software y
  versión (`uq_software_version`); no se permite duplicar esa combinación.
- El tipo de licencia admite: Perpetua, Suscripción, OEM, Volumen y Libre /
  Open Source.
- Los campos requeridos son software, versión, tipo de licencia y licencias
  totales; descripción, fecha de expiración y costo anual son opcionales
  (costo anual por defecto 0.00).
- El listado (`/productos`) muestra licencias totales, usadas y disponibles
  por producto, con filtros por texto (nombre/versión) y tipo de licencia.
- El detalle de un producto incluye los equipos donde está instalado
  (vista de instalaciones asociadas).
- `licencias_usadas` y `licencias_disponibles` se calculan a partir de las
  instalaciones vigentes (no eliminadas lógicamente) del producto.
- La eliminación es un borrado lógico (`is_deleted=True`); un producto con
  instalaciones vigentes no puede eliminarse.
- Cada alta, modificación y baja genera un evento de auditoría
  (`software.alta`, `software.actualizacion`, `software.baja`).

## Reglas de negocio

- No se puede reducir `licencias_totales` por debajo de la cantidad de
  instalaciones vigentes del producto.
- No se puede eliminar un producto que tenga instalaciones vigentes; primero
  deben eliminarse o reasignarse esas instalaciones.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET /api/v1/software/productos/` |
| API | `POST /api/v1/software/productos/` |
| API | `GET /api/v1/software/productos/{id}/` |
| API | `PATCH /api/v1/software/productos/{id}/` |
| API | `DELETE /api/v1/software/productos/{id}/` |
| API | `GET /api/v1/software/productos/estadisticas/` |
| API | `GET /api/v1/software/productos/opciones/` |
| Backend | `backend/software/repositories/producto_software_repository.py` |
| Backend | `backend/software/services/producto_software_service.py` |
| Backend | `backend/software/serializers/producto_software_serializers.py` |
| Backend | `backend/software/views/producto_software_views.py` |
