# HU-USUARIOS-001: Administrar cuentas institucionales

| Campo | Valor |
|-------|-------|
| Módulo | Usuarios |
| Prioridad | Alta |
| Fecha | 2026-08-01 |
| Autor | Leonardo Jaren |
| Estado | En revisión |

## Historia

**Como** administrador de KairOs
**Quiero** gestionar cuentas, roles y estados
**Para** controlar de manera segura quién accede a las funciones institucionales

## Descripción

La pantalla presenta indicadores, filtros, tabla paginada y formularios modales. Los técnicos cuentan con un alcance reducido a usuarios docentes.

## Criterios de aceptación

- [x] **Dado** un administrador autenticado, **cuando** registra datos válidos, **entonces** se crea una cuenta sin exponer la contraseña.
- [x] **Dado** un correo existente, **cuando** se intenta reutilizar, **entonces** se muestra un error claro y no se crea otra cuenta.
- [x] **Dado** un técnico autenticado, **cuando** consulta usuarios, **entonces** solo recibe cuentas docentes.
- [x] **Dado** un administrador, **cuando** desactiva una cuenta, **entonces** se conserva el registro y se impide su acceso.

## Alcance técnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `GET/POST /api/v1/usuarios/` |
| Service | `backend/usuarios/services/usuario_service.py` |
| Repository | `backend/usuarios/repositories/usuario_repository.py` |
| Frontend | `frontend/src/composables/usuarios/useUsuarios.js` |

## RF / RNF relacionados

- RF: `RF-USUARIOS-001`
- RNF: `RNF-USUARIOS-001`

## Notas de implementación

Se corrigió la migración de `apellido` y `dni`, se añadieron filtros y estadísticas, y se implementó desactivación segura.

## Enlaces

- PR: N/A
- Issue GitHub: N/A
