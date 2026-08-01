# Instrucciones para GitHub Copilot — KairOs

Lee y aplica `docs/CONTRIBUCION-IA.md` como referencia completa. Resumen obligatorio:

## Proyecto

Monorepo KairOs: `backend/` (Django 6 + DRF), `frontend/` (Vue 3). Esta guia prioriza **backend** salvo que el usuario indique frontend (ver `AGENTS.md`).

## Arquitectura backend (obligatorio)

Capas: **ViewSet/APIView → Serializer → Service → Repository → Model**.

- Usar siempre `shared/`: `BaseModel`, `BaseRepository`, `BaseService`, `BaseViewSet`.
- App de referencia: `backend/usuarios/`.
- Aplicar **SOLID**: logica de negocio solo en Services; ORM solo en Repositories.
- No saltar capas ni duplicar CRUD generico.

## Codigo

- Nombres de dominio en **espanol** (`correo`, `nombre`, `EquipoRepository`).
- Docstrings y comentarios en espanol, sin emojis; explicar funcionalidad, no obviedades.
- Serializers separados para lectura/escritura cuando aplique.
- Registrar nuevos endpoints en `backend/server/urls.py`.

## Ramas Git

Formato: `{ANIO}{InicialNombre}{InicialApellido}_{MesAbrev}{Dia}_{descripcion-kebab}`

Ejemplo: `2026WS_Jun28_listar-equipos`

Leer iniciales de `.github/developer-config.json` si existe.

## Documentacion funcional

Al implementar un flujo (ej. listar equipos), crear archivos en:

- `docs/requerimientos-funcionales/<modulo>-<slug>.md`
- `docs/requerimientos-no-funcionales/<modulo>-<slug>.md`
- `docs/historias-de-usuario/<modulo>-<slug>.md`

Usar plantillas en `docs/plantillas/`. Nombrar archivos en kebab-case.

## Cuando el usuario diga "sube el PR" o "crea el PR"

1. Confirmar que hay cambios commiteados.
2. Ejecutar desde la raiz del repo:

```powershell
.\scripts\create-pr-and-project.ps1 -Descripcion "<slug>" -Modulo "<modulo>" -HistoriaTitulo "<titulo>"
```

En Linux/macOS:

```bash
./scripts/create-pr-and-project.sh --descripcion "<slug>" --modulo "<modulo>" --historia-titulo "<titulo>"
```

3. El script crea el PR, un issue tipo historia de usuario y lo agrega al GitHub Project (si esta configurado).
4. No hacer push a `main` directamente.

## Pull requests

Usar plantilla `.github/pull_request_template.md`. Titulo descriptivo sin prefijo de fecha/iniciales.

## Checklist al terminar una tarea

- Capas y `shared/` respetados
- Docstrings en metodos publicos
- Docs en `docs/` si es flujo funcional
- Rama con convencion del equipo
