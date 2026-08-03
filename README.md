# KairOs

KairOs es una plataforma integral de gestión de activos y control operativo para laboratorios de cómputo. Diseñada bajo un enfoque de IT Asset Management (ITAM), el sistema optimiza la disponibilidad de recursos tecnológicos, asegurando que el hardware y software estén operativos en el momento preciso.

## Stack tecnológico

- **Backend:** Django 6 + Django REST Framework + SimpleJWT + PostgreSQL.
- **Frontend:** Vue 3 (Vite) + Tailwind CSS v4 + Pinia + Vue Router + Axios + Lucide.
- **Autenticación:** JWT con refresh silencioso, login tradicional y login con Google.

## Estado de los módulos

| Módulo | Backend | Frontend | Descripción |
|---|---|---|---|
| Autenticación | ✅ | ✅ | Login, recuperación de contraseña, login con Google, refresh de tokens. |
| Usuarios | ✅ | ✅ | CRUD de usuarios, roles (admin, técnico, docente, usuario) y perfil técnico. |
| Espacios | ✅ | ✅ | Gestión de laboratorios/aulas y asignación de usuarios por espacio. |
| Equipos | ✅ | ✅ | Inventario de hardware: alta, edición, retiro (borrado lógico), filtros e indicadores. |
| Mantenimiento | ✅ | ✅ | Tickets de mantenimiento preventivo/correctivo asociados a equipos y técnicos. |
| Software | ⏳ | ⏳ | Modelos base creados; endpoints y pantalla pendientes. |
| Incidencias | ⏳ | ⏳ | Modelos base creados; endpoints y pantalla pendientes. |
| Historial | ⏳ | ⏳ | Modelos base creados; endpoints y pantalla pendientes. |

## Arquitectura

### Backend (`backend/`)

Cada módulo (app Django) sigue una arquitectura en capas obligatoria:

```
URL → ViewSet/APIView → Serializer → Service → Repository → Model
```

Estructura estándar de una app:

```
backend/<app>/
├── models.py
├── repositories/<entidad>_repository.py
├── services/<entidad>_service.py
├── serializers/<entidad>_serializers.py
├── views/<entidad>_views.py
├── urls/__init__.py
└── migrations/
```

Las clases base compartidas (`BaseModel`, `BaseRepository`, `BaseService`, `BaseViewSet`) viven en `backend/shared/` y deben reutilizarse en todo módulo CRUD nuevo.

App de referencia: `backend/usuarios/`.

### Frontend (`frontend/`)

Arquitectura en capas con Vue 3 + Tailwind CSS v4:

- `src/views/`: pantallas por módulo funcional.
- `src/composables/[modulo]/use[Nombre].js`: toda la lógica de estado y llamadas a servicios.
- `src/services/`: clientes Axios por dominio, alineados con las apps del backend.
- `src/components/`: componentes reutilizables agrupados por tipo (`buttons/`, `inputs/`, `tables/`, `selects/`, `modals/`, `cards/`, `toasts/`).
- `src/stores/`: estado global con Pinia.
- `src/router/`: rutas protegidas por autenticación y rol (`meta.requiresAuth`, `meta.roles`).

Consulta [`AGENTS.md`](AGENTS.md) para las reglas completas de codificación frontend (colores, alias `@`, iconografía, etc.).

## Puesta en marcha local

### 1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Completa DB_NAME, DB_USER, DB_PASSWORD, etc. en .env
python manage.py migrate
python manage.py runserver
```

Requiere una base de datos PostgreSQL local (`kairos_db` por defecto).

### 2. Datos de prueba

```powershell
# Usuario administrador (correo: admin@kairos.test / contraseña: Admin123!)
python manage.py crear_admin_prueba

# Espacios, equipos, técnicos y mantenimientos de ejemplo
python manage.py seed_datos_prueba
```

Ambos comandos son idempotentes: pueden ejecutarse varias veces sin duplicar datos.

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

La aplicación queda disponible en `http://localhost:5173/` y consume la API en `http://127.0.0.1:8000/api/v1/`.

### 4. Verificación

```powershell
# Backend
cd backend
python manage.py test

# Frontend
cd frontend
npm run build
npm run test
```

## Documentación

La documentación funcional y de proceso vive en [`docs/`](docs/):

| Carpeta | Contenido |
|---|---|
| `docs/requerimientos-funcionales/` | Requerimientos funcionales (RF) por módulo |
| `docs/requerimientos-no-funcionales/` | Requerimientos no funcionales (RNF) |
| `docs/historias-de-usuario/` | Historias de usuario (HU) |
| `docs/plantillas/` | Plantillas Markdown para nuevos documentos |

Guía completa de contribución (arquitectura, convenciones, ramas y flujo de PR): [`docs/CONTRIBUCION-IA.md`](docs/CONTRIBUCION-IA.md).

## Flujo de trabajo (ramas y PR)

Formato de rama: `{ANIO}{InicialNombre}{InicialApellido}_{MesAbrev}{Dia}_{descripcion-kebab}` (ej. `2026WS_Jun28_listar-equipos`).

Configuración inicial de cada desarrollador (iniciales, GitHub Project, `gh auth login`): ver [`.github/README.md`](.github/README.md).

Para abrir un PR con su historia de usuario asociada:

```powershell
.\scripts\create-pr-and-project.ps1 -Descripcion "<slug>" -Modulo "<modulo>" -HistoriaTitulo "<titulo>"
```

## Instrucciones para agentes de IA

- Backend: [`docs/CONTRIBUCION-IA.md`](docs/CONTRIBUCION-IA.md) y [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
- Frontend: [`AGENTS.md`](AGENTS.md).
