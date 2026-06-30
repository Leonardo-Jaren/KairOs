# Guia de contribucion con IA — KairOs (Backend)

Documento canonico para agentes de IA y desarrolladores. Las instrucciones de GitHub Copilot (`.github/copilot-instructions.md`) y las reglas de Cursor (`.cursor/rules/`) deben alinearse con este archivo.

Para el frontend, ver `AGENTS.md` en la raiz del repositorio.

---

## 1. Stack y estructura

- **Backend:** Django 6 + Django REST Framework + SimpleJWT + PostgreSQL.
- **Raiz del codigo:** `backend/`
- **Configuracion Django:** `backend/server/`
- **Clases base compartidas:** `backend/shared/`
- **Modulos de dominio:** apps Django en espanol y plural (`usuarios`, `equipos`, `espacios`, etc.)

### Estructura de cada app (CRUD)

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

**App de referencia:** `backend/usuarios/` (implementacion completa).

---

## 2. Arquitectura en capas (obligatorio)

Flujo: **URL → ViewSet/APIView → Serializer → Service → Repository → Model**

| Capa | Responsabilidad | Prohibido |
|------|-----------------|-----------|
| **Model** | Entidades ORM, relaciones, `Meta` | Logica de negocio, queries complejas en views |
| **Repository** | Acceso a datos (ORM) | Reglas de negocio, validaciones HTTP |
| **Service** | Logica de negocio | Acceso directo al ORM sin repository |
| **ViewSet** | HTTP, permisos, eleccion de serializer | Logica de negocio inline |
| **Serializer** | Validacion y forma de entrada/salida | Logica de persistencia |

### Principios SOLID

- **S (Single Responsibility):** Una clase, una razon de cambio. Ejemplo: `UsuarioRepository` solo consulta/guarda; `UsuarioService` aplica reglas.
- **O (Open/Closed):** Extender via herencia en `shared/`, no modificar bases sin necesidad.
- **L (Liskov):** Subclases de `BaseRepository`, `BaseService`, `BaseViewSet` deben respetar el contrato de la base.
- **I (Interface Segregation):** Serializers separados para lectura y escritura cuando aplique (`UsuarioSerializer` vs `UsuarioCreateUpdateSerializer`).
- **D (Dependency Inversion):** Views dependen de Services; Services dependen de Repositories, no de ORM en views.

---

## 3. Uso obligatorio de `shared/`

Siempre que exista una base aplicable, usar:

| Necesidad | Importar desde |
|-----------|----------------|
| Modelo con auditoria | `shared.models.BaseModel` |
| CRUD de datos | `shared.base_repository.BaseRepository` |
| Logica CRUD estandar | `shared.base_service.BaseService` |
| API REST CRUD | `shared.base_viewset.BaseViewSet` |

No reimplementar CRUD generico en cada app. Sobrescribir solo metodos especificos del dominio.

**Excepcion valida:** `autenticacion/` usa `APIView` para login/password (flujos no CRUD).

---

## 4. Convenciones de nombres

| Elemento | Convencion | Ejemplo |
|----------|------------|---------|
| App Django | espanol, plural, minusculas | `equipos` |
| Clase modelo | PascalCase, singular | `Equipo` |
| Repository/Service/ViewSet | `{Entidad}Repository` etc. | `EquipoRepository` |
| Archivos | `{entidad}_{capa}.py` | `equipo_service.py` |
| Campos de dominio | espanol | `correo`, `nombre`, `codigo` |
| API prefix | `api/v1/<modulo>/` | `api/v1/equipos/` |
| Ramas Git | ver seccion 6 | `2026WS_Jun28_listar-equipos` |

---

## 5. Comentarios y docstrings

- Redactar en **espanol**, sin emojis.
- Docstrings en clases y metodos publicos: explicar **que hace** y **por que**, no repetir el nombre del metodo.
- Comentarios inline solo para reglas de negocio no obvias.

Ejemplo correcto (ver `backend/usuarios/views/usuario_views.py`):

```python
def get_serializer_class(self):
    """
    Retorna dinamicamente el serializador apropiado:
    - UsuarioCreateUpdateSerializer para acciones de escritura.
    - UsuarioSerializer para acciones de lectura.
    """
```

---

## 6. Convencion de ramas y pull requests

### Formato de rama

```
{ANIO}{InicialNombre}{InicialApellido}_{MesAbrev}{Dia}_{descripcion-kebab}
```

Ejemplo: `2026WS_Jun28_listar-equipos`

- **ANIO:** 4 digitos (ej. `2026`)
- **Iniciales:** primera letra del nombre + primera del apellido en MAYUSCULA (ej. `WS`)
- **Fecha:** mes en ingles abreviado (3 letras) + dia sin cero a la izquierda (ej. `Jun28`)
- **descripcion:** kebab-case, corta y descriptiva

Configurar iniciales en `.github/developer-config.json` (copiar desde `developer-config.example.json`).

### Pull request

- Titulo: mismo slug descriptivo de la rama (sin prefijo de fecha/iniciales).
- Cuerpo: usar la plantilla en `.github/pull_request_template.md`.
- Base: `main` salvo indicacion contraria.

### Comando rapido (PowerShell)

```powershell
.\scripts\create-pr-and-project.ps1 -Descripcion "listar-equipos" -Modulo equipos -HistoriaTitulo "Listar equipos del laboratorio"
```

---

## 7. Documentacion funcional en `docs/`

Al implementar o modificar un **flujo funcional** (endpoint, caso de uso, pantalla relacionada), crear o actualizar documentacion en:

| Carpeta | Contenido |
|---------|-----------|
| `docs/requerimientos-funcionales/` | RF del modulo |
| `docs/requerimientos-no-funcionales/` | RNF (rendimiento, seguridad, etc.) |
| `docs/historias-de-usuario/` | Historias de usuario |

### Convencion de archivos

```
docs/<tipo>/<modulo>-<slug>.md
```

Ejemplo: `docs/historias-de-usuario/equipos-listar-equipos.md`

Usar plantillas en `docs/plantillas/`. No dejar secciones vacias: escribir "N/A" si no aplica.

### Cuando generar docs

- Al cerrar un flujo nuevo (ej. listar equipos).
- Cuando el usuario o la tarea lo indique explicitamente.
- Antes de abrir PR si el cambio introduce comportamiento visible para el usuario.

---

## 8. Flujo "sube el PR" + GitHub Projects

Cuando el usuario pida **subir el PR**, **crear PR** o equivalente:

1. Verificar cambios commiteados en la rama actual.
2. Ejecutar `scripts/create-pr-and-project.ps1` (Windows) o `scripts/create-pr-and-project.sh` (Linux/macOS).
3. El script:
   - Crea o usa la rama con formato correcto.
   - Abre el PR con plantilla estandar.
   - Crea una **historia de usuario** como issue en GitHub.
   - Agrega el issue al Project configurado en `.github/project-config.json`.

Requisitos previos: [GitHub CLI](https://cli.github.com/) (`gh`) autenticado (`gh auth login`) y `project-config.json` configurado (copiar desde `project-config.example.json`).

---

## 9. Checklist antes de entregar codigo

- [ ] Capas respetadas (View → Service → Repository → Model)
- [ ] Herencia desde `shared/` donde corresponda
- [ ] Nombres en espanol y consistentes con `usuarios/`
- [ ] Docstrings en metodos publicos
- [ ] URLs registradas en `backend/server/urls.py` si es endpoint nuevo
- [ ] Documentacion en `docs/` si es flujo funcional
- [ ] Rama y PR siguen convencion del equipo
