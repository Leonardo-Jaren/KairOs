# Configuracion local de GitHub (KairOs)

Guia de **configuracion unica por desarrollador** para el flujo de ramas, PRs y GitHub Projects (`scripts/create-pr-and-project.ps1` / `.sh`).

Los archivos personales (`developer-config.json` y `project-config.json`) estan en `.gitignore` y no se suben al repositorio.

---

## Configuracion que debe hacer cada dev (una vez)

### 1. Iniciales para ramas

Formato de rama: `2026WS_Jun28_ejemplo` (ver `docs/CONTRIBUCION-IA.md`).

**Windows (PowerShell):**

```powershell
Copy-Item .github\developer-config.example.json .github\developer-config.json
# Editar authorInitials y fullName
```

**Linux / macOS:**

```bash
cp .github/developer-config.example.json .github/developer-config.json
# Editar authorInitials y fullName
```

Ejemplo:

```json
{
  "authorInitials": "WS",
  "fullName": "Nombre Apellido"
}
```

### 2. GitHub Project (flujo "sube el PR")

**Windows (PowerShell):**

```powershell
Copy-Item .github\project-config.example.json .github\project-config.json
# Completar projectNumber (ver seccion siguiente)
```

**Linux / macOS:**

```bash
cp .github/project-config.example.json .github/project-config.json
# Completar projectNumber (ver seccion siguiente)
```

### 3. GitHub CLI

Instalar [GitHub CLI](https://cli.github.com/) y autenticarse:

```bash
gh auth login
```

El script valida que `gh` este disponible; si no esta instalado, falla con un mensaje claro.

---

## Obtener el numero del Project (`projectNumber`)

1. Abre el GitHub Project del equipo en el navegador.
2. La URL tiene la forma:
   - `https://github.com/users/{owner}/projects/{number}`
   - `https://github.com/orgs/{org}/projects/{number}`
3. Usa ese `{number}` en `projectNumber` dentro de `.github/project-config.json`.

Ejemplo de `project-config.json`:

```json
{
  "owner": "Leonardo-Jaren",
  "repo": "KairOs",
  "projectNumber": 1,
  "baseBranch": "main",
  "issueLabels": ["historia-de-usuario", "kairos"]
}
```

---

## Como lo usan tus colegas en VS Code

1. **Abrir la carpeta raiz `KairOs`** (monorepo completo), no solo `backend/` ni `frontend/`.
2. **GitHub Copilot** lee automaticamente [`.github/copilot-instructions.md`](copilot-instructions.md) al trabajar en el repo.
3. **Al pedir un flujo** (ej. listar equipos), Copilot debe generar documentacion en `docs/` usando las plantillas de `docs/plantillas/`:
   - `docs/requerimientos-funcionales/<modulo>-<slug>.md`
   - `docs/requerimientos-no-funcionales/<modulo>-<slug>.md`
   - `docs/historias-de-usuario/<modulo>-<slug>.md`
4. **Al decir "sube el PR"** (con cambios ya commiteados), ejecutar desde la raiz:

```powershell
.\scripts\create-pr-and-project.ps1 -Descripcion "listar-equipos" -Modulo equipos -HistoriaTitulo "Listar equipos del laboratorio"
```

En Linux / macOS:

```bash
./scripts/create-pr-and-project.sh --descripcion "listar-equipos" --modulo equipos --historia-titulo "Listar equipos del laboratorio"
```

Eso hace **push**, crea el **PR**, abre un **issue** tipo historia de usuario y lo agrega al **Project** (si `projectNumber` esta configurado en `project-config.json`).

---

## Verificacion rapida

Desde la raiz del repositorio, con los tres pasos hechos:

```powershell
.\scripts\create-pr-and-project.ps1 -Descripcion "ejemplo" -Modulo equipos -HistoriaTitulo "Ejemplo de prueba" -DryRun
```

`-DryRun` muestra rama, PR e issue sin ejecutar cambios. Quita el flag cuando quieras crear el PR de verdad.

---

## Referencias

- Flujo completo (ramas, docs, PR): `docs/CONTRIBUCION-IA.md`
- Instrucciones para Copilot: `.github/copilot-instructions.md`
- Plantilla de PR: `.github/pull_request_template.md`
