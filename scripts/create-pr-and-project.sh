#!/usr/bin/env bash
# Crea push, PR e issue de historia de usuario en GitHub Projects.
# Uso: ./scripts/create-pr-and-project.sh --descripcion listar-equipos --modulo equipos --historia-titulo "Listar equipos"
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DESCRIPCION=""
MODULO=""
HISTORIA_TITULO=""
AUTHOR_INITIALS=""
BASE_BRANCH=""
SKIP_BRANCH=0
DRY_RUN=0

usage() {
  echo "Uso: $0 --descripcion <slug> --modulo <modulo> --historia-titulo <titulo> [--author-initials WS] [--base-branch main] [--skip-branch] [--dry-run]"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --descripcion) DESCRIPCION="$2"; shift 2 ;;
    --modulo) MODULO="$2"; shift 2 ;;
    --historia-titulo) HISTORIA_TITULO="$2"; shift 2 ;;
    --author-initials) AUTHOR_INITIALS="$2"; shift 2 ;;
    --base-branch) BASE_BRANCH="$2"; shift 2 ;;
    --skip-branch) SKIP_BRANCH=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) usage ;;
  esac
done

[[ -n "$DESCRIPCION" && -n "$MODULO" && -n "$HISTORIA_TITULO" ]] || usage

step() { echo "==> $1"; }

read_json_field() {
  local file="$1" field="$2"
  [[ -f "$file" ]] || return 1
  python3 - "$file" "$field" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data.get(sys.argv[2], ""))
PY
}

slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//'
}

get_initials() {
  if [[ -n "$AUTHOR_INITIALS" ]]; then
    echo "$AUTHOR_INITIALS" | tr '[:lower:]' '[:upper:]'
    return
  fi
  local from_file
  from_file="$(read_json_field "$REPO_ROOT/.github/developer-config.json" authorInitials || true)"
  if [[ -n "$from_file" ]]; then
    echo "$from_file" | tr '[:lower:]' '[:upper:]'
    return
  fi
  echo "Define iniciales con --author-initials o .github/developer-config.json" >&2
  exit 1
}

branch_name() {
  local initials="$1" slug="$2"
  local month day year
  month="$(date +%b)"
  day="$(date +%-d 2>/dev/null || date +%d | sed 's/^0//')"
  year="$(date +%Y)"
  echo "${year}${initials}_${month}${day}_${slug}"
}

change_summary() {
  local base="${BASE_BRANCH:-main}"
  {
    git -C "$REPO_ROOT" log "${base}..HEAD" --pretty=format:'- %s' 2>/dev/null || true
    echo
    echo "### Archivos modificados"
    echo '```'
    git -C "$REPO_ROOT" diff "${base}...HEAD" --stat 2>/dev/null || true
    echo '```'
  }
}

command -v gh >/dev/null 2>&1 || { echo "Instala GitHub CLI: https://cli.github.com/"; exit 1; }

PROJECT_FILE="$REPO_ROOT/.github/project-config.json"
[[ -f "$PROJECT_FILE" ]] || PROJECT_FILE="$REPO_ROOT/.github/project-config.example.json"

if [[ -z "$BASE_BRANCH" ]]; then
  BASE_BRANCH="$(read_json_field "$PROJECT_FILE" baseBranch || echo main)"
fi
[[ -n "$BASE_BRANCH" ]] || BASE_BRANCH="main"

INITIALS="$(get_initials)"
SLUG="$(slugify "$DESCRIPCION")"
BRANCH="$(branch_name "$INITIALS" "$SLUG")"
CURRENT="$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)"

cd "$REPO_ROOT"

if [[ "$SKIP_BRANCH" -eq 0 && "$CURRENT" == "$BASE_BRANCH" ]]; then
  step "Creando rama $BRANCH"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    git checkout -b "$BRANCH"
    CURRENT="$BRANCH"
  fi
else
  step "Usando rama actual: $CURRENT"
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Hay cambios sin commitear." >&2
  exit 1
fi

step "Publicando rama $CURRENT"
if [[ "$DRY_RUN" -eq 0 ]]; then
  git push -u origin "$CURRENT"
fi

PR_BODY_FILE="$(mktemp)"
cat >"$PR_BODY_FILE" <<EOF
## Descripcion

$HISTORIA_TITULO

Modulo: **$MODULO**

Generado con \`scripts/create-pr-and-project.sh\`.

## Checklist

- [ ] Capas y shared/ respetados
- [ ] Documentacion en docs/ actualizada
EOF

step "Creando pull request"
if [[ "$DRY_RUN" -eq 1 ]]; then
  PR_URL="https://github.com/OWNER/REPO/pull/DRY-RUN"
else
  PR_URL="$(gh pr create --base "$BASE_BRANCH" --head "$CURRENT" --title "$HISTORIA_TITULO" --body-file "$PR_BODY_FILE")"
fi
rm -f "$PR_BODY_FILE"
echo "PR: $PR_URL"

ISSUE_BODY_FILE="$(mktemp)"
{
  echo "## Historia"
  echo
  echo "**Como** usuario del sistema KairOs"
  echo "**Quiero** $HISTORIA_TITULO"
  echo "**Para** gestionar correctamente el modulo $MODULO"
  echo
  echo "## Resumen de implementacion"
  echo
  change_summary
  echo
  echo "## Pull Request"
  echo "$PR_URL"
} >"$ISSUE_BODY_FILE"

step "Creando issue (historia de usuario)"
LABELS="$(read_json_field "$PROJECT_FILE" issueLabels || true)"
ISSUE_ARGS=(issue create --title "HU: $HISTORIA_TITULO" --body-file "$ISSUE_BODY_FILE")
if [[ -n "$LABELS" ]]; then
  # issueLabels as JSON array - simplified: use default labels from config if comma-separated in env
  :
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  ISSUE_URL="https://github.com/OWNER/REPO/issues/DRY-RUN"
else
  ISSUE_URL="$(gh issue create --title "HU: $HISTORIA_TITULO" --body-file "$ISSUE_BODY_FILE")"
fi
rm -f "$ISSUE_BODY_FILE"
echo "Issue: $ISSUE_URL"

PROJECT_NUMBER="$(read_json_field "$PROJECT_FILE" projectNumber || true)"
OWNER="$(read_json_field "$PROJECT_FILE" owner || true)"
if [[ -n "$PROJECT_NUMBER" && "$PROJECT_NUMBER" != "None" && -n "$OWNER" ]]; then
  step "Agregando issue al GitHub Project #$PROJECT_NUMBER"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$ISSUE_URL"
  fi
else
  echo "Advertencia: configura projectNumber en .github/project-config.json" >&2
fi

step "Listo"
