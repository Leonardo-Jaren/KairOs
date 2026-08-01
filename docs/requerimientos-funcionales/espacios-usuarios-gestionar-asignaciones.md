# RF-ESPACIOS-USUARIOS-001: Gestionar asignaciones de usuarios a espacios

| Campo | Valor |
|-------|-------|
| Módulo | EspaciosUsuarios |
| Versión | 1.0 |
| Fecha | 2026-08-01 |
| Autor | Leonardo Jaren |
| Estado | En revisión |

## Descripción

El sistema debe relacionar usuarios activos con espacios vigentes, indicando si participan como responsables, soporte técnico o docentes asignados.

## Actores

- Administrador
- Técnico

## Precondiciones

- El usuario y el espacio existen y están vigentes.
- El operador inició sesión.

## Flujo principal

1. El operador ingresa a Usuarios por espacio.
2. El sistema lista asignaciones con usuario, espacio, responsabilidad y estado.
3. El administrador abre el formulario de asignación.
4. El sistema consulta usuarios y espacios vigentes en páginas de 10 registros.
5. El administrador puede buscar y navegar entre páginas antes de seleccionar usuario y espacio.
6. Selecciona la responsabilidad.
7. El sistema valida las relaciones y evita duplicados.
8. La asignación se guarda con auditoría de creación y actualización.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Usuario inactivo o inexistente | Rechazar la asignación con respuesta 400. |
| Espacio eliminado o inexistente | Rechazar la asignación con respuesta 400. |
| Par usuario–espacio repetido | Informar que la asignación ya existe. |
| Técnico intenta modificar | Responder 403 y conservar la información. |

## Reglas de negocio

- Un usuario solo puede tener una asignación por espacio.
- El administrador dispone de CRUD lógico completo.
- El técnico dispone de acceso de solo lectura.
- La eliminación es lógica y conserva autor y fechas de auditoría.
- Este flujo no implementa el CRUD general de espacios.

## Criterios de aceptación

- [x] Se pueden buscar asignaciones por usuario, correo, espacio o pabellón.
- [x] La respuesta expande los datos mínimos del usuario y el espacio.
- [x] Los duplicados se rechazan.
- [x] Las opciones del formulario contienen únicamente registros vigentes.
- [x] Los catálogos de usuarios y espacios se consultan en páginas de 10 registros con búsqueda remota.
- [x] La eliminación lógica oculta la asignación de listados posteriores.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET/POST /api/v1/espacios/usuarios/` |
| API | `PATCH/DELETE /api/v1/espacios/usuarios/{id}/` |
| API | `GET /api/v1/espacios/usuarios/opciones/` |
| API | `GET /api/v1/usuarios/?page={n}&page_size=10&search={texto}` |
| API | `GET /api/v1/espacios/?page={n}&page_size=10&search={texto}` |
| Backend | `backend/espacios/` |
| Frontend | `frontend/src/views/espacios/EspaciosUsuariosView.vue` |
| Componente | `frontend/src/components/selects/BasePaginatedSelect.vue` |

## Notas

El módulo reutiliza el modelo `Espacio` existente, sin asumir la implementación del listado general asignada a otro integrante.
