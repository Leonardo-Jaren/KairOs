# HU-ESPACIOS-USUARIOS-001: Asignar responsables a espacios

| Campo | Valor |
|-------|-------|
| Módulo | EspaciosUsuarios |
| Prioridad | Alta |
| Fecha | 2026-08-01 |
| Autor | Leonardo Jaren |
| Estado | En revisión |

## Historia

**Como** administrador de KairOs
**Quiero** asignar usuarios responsables a los espacios institucionales
**Para** identificar claramente quién atiende y utiliza cada ambiente

## Descripción

El flujo vincula cuentas y espacios existentes sin reemplazar el módulo de listado de espacios. La interfaz permite buscar, crear, editar y retirar asignaciones con permisos diferenciados.

## Criterios de aceptación

- [x] **Dado** un usuario y un espacio vigentes, **cuando** el administrador registra una responsabilidad, **entonces** se crea una asignación auditada.
- [x] **Dado** un par ya registrado, **cuando** se intenta repetir, **entonces** se rechaza sin duplicar información.
- [x] **Dado** un técnico autenticado, **cuando** consulta asignaciones, **entonces** puede visualizarlas pero no modificarlas.
- [x] **Dado** una asignación retirada, **cuando** se consulta la lista, **entonces** deja de aparecer y permanece en la base para auditoría.
- [x] **Dado** que existen más de 10 usuarios o espacios, **cuando** el administrador abre el selector, **entonces** puede buscar y navegar por páginas sin cargar el catálogo completo.

## Alcance técnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `GET/POST /api/v1/espacios/usuarios/` |
| Service | `backend/espacios/services/espacio_usuario_service.py` |
| Repository | `backend/espacios/repositories/espacio_usuario_repository.py` |
| Frontend | `frontend/src/composables/espacios/useEspaciosUsuarios.js` |
| Componente | `frontend/src/components/selects/BasePaginatedSelect.vue` |

## RF / RNF relacionados

- RF: `RF-ESPACIOS-USUARIOS-001`
- RNF: `RNF-ESPACIOS-USUARIOS-001`

## Notas de implementación

Se añadió `EspacioUsuario` con restricción única, auditoría, borrado lógico, filtros y selectores remotos paginados para catálogos grandes.

## Enlaces

- PR: N/A
- Issue GitHub: N/A
