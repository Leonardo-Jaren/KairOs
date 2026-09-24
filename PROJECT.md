# Project: Territorial Scope Assignments & Organigrama Integration (KairOs)

## Architecture
KairOs is a full-stack facility and maintenance management system:
- **Backend**: Django 5 + Django REST Framework (DRF) in `backend/`. Layered architecture: Model -> Repository -> Service -> Serializer -> ViewSet -> URL.
- **Frontend**: Vue 3 (Vite) + Pinia + Tailwind CSS v4 + Lucide Vue in `frontend/src/`. Thin views, logic extracted into composables (`src/composables/`), centralized API services (`src/services/`).
- **Data Flow**:
  - Territorial scopes: `Local` (Sede) -> `Edificio` (Pabellón) -> `Piso` (Floor string on Edificio/Espacio) -> `Espacio` (Room).
  - Territorial Assignment entity: `EspacioUsuario` extended to cover 4 scopes (`ambito` in `['sede', 'edificio', 'piso', 'espacio']`).
  - Supervisor line of command: `Usuario.supervisor` (self-referential FK). Auto-associated with active `responsable` of the assigned sede when a technician without supervisor receives a territorial assignment.
  - Security & Permissions: Superadmin/admin have universal access; Responsable has scoped access limited to assigned physical sedes (`UsuarioSede`), rejecting foreign sedes with HTTP 403; Tecnico/docente have read-only access.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Modelo de Asignación a 4 Ámbitos | Extensión de `EspacioUsuario` con `ambito` (`sede`, `edificio`, `piso`, `espacio`), claves foráneas opcionales y unicidad activa | M1 | R1, survey |
| 2 | CRUD y Serialización de Asignaciones | Endpoints DRF `/api/v1/espacios/usuarios/` con soporte de lectura y escritura para los 4 niveles territoriales | M1 | R1, survey |
| 3 | Autorización por Sede y Restricción 403 | Permiso `CanManageEspacioUsuario` que valida sedes asignadas al rol `responsable` y rechaza sedes foráneas con HTTP 403 | M1 | R5, survey |
| 4 | No Exclusividad Colaborativa | Garantía operativa de que las asignaciones son referenciales y no bloquean el trabajo de otros técnicos de la sede | M1 | R2, survey |
| 5 | Auto-asociación Inteligente de Supervisor | Vinculación automática del responsable activo de sede como supervisor de técnicos sin supervisor asignado | M2 | R3, survey |
| 6 | Preservación de Jerarquía Existente | Mantenimiento intacto del supervisor previo si el técnico ya contaba con uno antes de la asignación | M2 | R3, survey |
| 7 | Reporte de Encargados Heredados | Consulta de espacios que reporta tanto encargados directos como heredados (piso, pabellón, sede) | M2 | R4, survey |
| 8 | Badges de Ámbitos en Organigrama (Backend) | Inyección de `asignaciones_territoriales` en los nodos del endpoint `/api/v1/usuarios/organigrama/` | M2 | R3, survey |
| 9 | Modal con Selector en Cascada | Formulario modal en `EspaciosUsuariosView.vue` con selección de nivel y cascada Sede -> Pabellón -> Piso -> Espacio | M3 | R4, survey |
| 10 | Tabla Centralizada y Filtros por Sede/Pabellón | Tabla paginada de asignaciones con filtros por Sede y Pabellón y renderizado compuesto del ámbito | M3 | R4, survey |
| 11 | Permisos en UI (`canEdit` extendido) | Habilitación de acciones de gestión en UI para `superadmin`, `admin` y `responsable` en sus sedes | M3 | R5, survey |
| 12 | Acción Contextual en Croquis/Campus | Visualización y asignación contextual del encargado de piso directamente en `CroquisPiso.vue` | M4 | R4, survey |
| 13 | Badges Territoriales en Nodos de Organigrama | Visualización gráfica de etiquetas distintivas de áreas a cargo en `OrgChartNode.vue` y `OrgUserDrawer.vue` | M4 | R3, survey |
| 14 | Verificación E2E y Suite de Pruebas | Suite de pruebas E2E multi-tier, pruebas unitarias backend y frontend, y endurecimiento adversarial | M5 / E2E | R1-R5, AC |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Track | Infraestructura y suite de pruebas E2E en 4 Tiers (Categoría-Partición, Límites, Cruces, Real-World) | none | DONE |
| 1 | M1: Backend Data Model, Validations & Scope API | Extensión de `EspacioUsuario`, migración DB, `EspacioUsuarioService`, `CanManageEspacioUsuario` con HTTP 403 por sede, tests unitarios backend | none | DONE |
| 2 | M2: Organigrama Integration, Auto-Supervisor & Inherited | Auto-asociación de supervisor responsable de sede, preservación de supervisor existente, encargados heredados en espacios, payload de badges en organigrama | M1 | DONE |
| 3 | M3: Frontend Centralized Table & Cascading Modal | `useEspaciosUsuarios.js` (refactor `canEdit`, estado en cascada), `EspaciosUsuariosView.vue` (modal 4 niveles, filtros sede/edificio, display compuesto), tests vitest | M1 | DONE |
| 4 | M4: Frontend Contextual Croquis & Organigrama Badges | `CroquisPiso.vue` (encargado de piso, modal contextual), `OrgChartNode.vue` y `OrgUserDrawer.vue` (badges territoriales), tests vitest | M2, M3 | DONE |
| 5 | M5: Final Integration & Verification | Ejecución de 100% pruebas E2E (Tiers 1-4), 88 pruebas unitarias preexistentes + nuevas, verificación adversarial (Tier 5) y Forensic Audit | M1, M2, M3, M4, E2E | DONE |

## Interface Contracts

### Backend API: `/api/v1/espacios/usuarios/`
- **POST / PUT Payload**:
  ```json
  {
    "usuario_id": 12,
    "tipo_responsabilidad": "tecnico",
    "ambito": "piso",
    "local_id": 1,
    "edificio_id": 2,
    "piso": "2",
    "espacio_id": null,
    "activo": true
  }
  ```
- **Rules**:
  - If `ambito == 'sede'`: requires `local_id`. `edificio_id`, `piso`, `espacio_id` are null.
  - If `ambito == 'edificio'`: requires `local_id`, `edificio_id`. `piso`, `espacio_id` are null.
  - If `ambito == 'piso'`: requires `local_id`, `edificio_id`, `piso`. `espacio_id` is null.
  - If `ambito == 'espacio'`: requires `espacio_id` (auto-populates `local_id`, `edificio_id`, `piso` from space).
  - Unicidad: Reject duplicate active assignment for same scope entity + user.
  - Authorization: If `request.user.rol == 'responsable'`, verify `local_id` in user's active sedes. If not -> HTTP 403 Forbidden.

### Backend API: `/api/v1/espacios/{id}/`
- **Response Extensions**:
  ```json
  {
    "id": 105,
    "codigo_espacio": "LAB-201",
    "encargados_directos": [
      { "id": 1, "usuario_nombre": "Carlos Perez", "tipo_responsabilidad": "tecnico" }
    ],
    "encargados_heredados": [
      { "id": 2, "usuario_nombre": "Ana Gomez", "tipo_responsabilidad": "tecnico", "origen": "Pabellón A · Piso 2" }
    ]
  }
  ```

### Backend API: `/api/v1/usuarios/organigrama/`
- **Node Extension**:
  ```json
  {
    "id": 12,
    "nombre": "Carlos Perez",
    "rol": "tecnico",
    "supervisor_id": 5,
    "supervisor_nombre": "Laura Mendez",
    "sedes": ["Sede Central"],
    "asignaciones_territoriales": [
      { "ambito": "piso", "badge": "Encargado Piso 2 · Pabellón A", "tipo_responsabilidad": "tecnico" }
    ],
    "children": [...]
  }
  ```

## Code Layout
- Backend Models: `backend/espacios/models.py`, `backend/usuarios/models.py`
- Backend Permissions: `backend/espacios/permissions.py`
- Backend Services: `backend/espacios/services/espacio_usuario_service.py`, `backend/usuarios/services/usuario_service.py`
- Backend Repositories: `backend/espacios/repositories/`, `backend/usuarios/repositories/usuario_repository.py`
- Backend Serializers: `backend/espacios/serializers/espacio_usuario_serializers.py`, `backend/espacios/serializers/espacio_serializers.py`
- Backend Views: `backend/espacios/views/espacio_usuario_views.py`, `backend/usuarios/views/usuario_views.py`
- Backend Tests: `backend/espacios/tests/`, `backend/usuarios/tests/`
- Frontend Views: `frontend/src/views/espacios/EspaciosUsuariosView.vue`, `frontend/src/views/espacios/CampusTecnologicoView.vue`, `frontend/src/views/usuarios/UsuariosView.vue`
- Frontend Composables: `frontend/src/composables/espacios/useEspaciosUsuarios.js`, `frontend/src/composables/usuarios/useOrganigrama.js`
- Frontend Components: `frontend/src/components/espacios/CroquisPiso.vue`, `frontend/src/components/organigrama/OrgChartNode.vue`, `frontend/src/components/organigrama/OrgUserDrawer.vue`
- Frontend Services: `frontend/src/services/espacios.service.js`, `frontend/src/services/usuarios.service.js`
- Frontend Tests: `frontend/src/composables/espacios/useEspaciosUsuarios.spec.js`, `frontend/src/composables/usuarios/useOrganigrama.spec.js`
