# RF-USUARIOS-001: Gestionar usuarios

| Campo | Valor |
|-------|-------|
| Módulo | Usuarios |
| Versión | 1.0 |
| Fecha | 2026-08-01 |
| Autor | Leonardo Jaren |
| Estado | En revisión |

## Descripción

El sistema debe permitir consultar, buscar, crear, actualizar y desactivar cuentas de usuario, aplicando permisos según el rol del operador.

## Actores

- Administrador
- Técnico

## Precondiciones

- El operador inició sesión con un token válido.
- El rol del operador es administrador o técnico.

## Flujo principal

1. El operador ingresa al módulo Usuarios.
2. El sistema muestra indicadores y una lista paginada sin campos sensibles.
3. El operador filtra por texto, rol o estado.
4. El operador registra o modifica una cuenta autorizada.
5. El sistema valida formato, unicidad y permisos antes de guardar.
6. La interfaz confirma el resultado y actualiza los datos.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Correo o username duplicado | Responder 400 con el campo que presenta el conflicto. |
| Técnico intenta gestionar un rol no docente | Rechazar la operación sin modificar información. |
| Operador no autenticado | Responder 401. |
| Desactivación de la propia cuenta | Rechazar la operación para evitar pérdida accidental de acceso. |

## Reglas de negocio

- El administrador puede gestionar todos los roles.
- El técnico únicamente puede listar y crear cuentas docentes.
- Las contraseñas nunca se devuelven por API y siempre se almacenan cifradas.
- La eliminación funcional desactiva la cuenta y conserva su historial.
- El DNI, cuando se registra, contiene exactamente ocho dígitos.

## Criterios de aceptación

- [x] La lista es paginada y permite búsqueda, rol y estado.
- [x] Las respuestas no incluyen contraseñas.
- [x] La creación cifra la contraseña.
- [x] Los permisos de administrador y técnico se verifican en backend y frontend.
- [x] La desactivación no elimina físicamente la cuenta.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API | `GET/POST /api/v1/usuarios/` |
| API | `PATCH/DELETE /api/v1/usuarios/{id}/` |
| API | `GET /api/v1/usuarios/estadisticas/` |
| Backend | `backend/usuarios/` |
| Frontend | `frontend/src/views/usuarios/UsuariosView.vue` |

## Notas

El endpoint DELETE aplica desactivación lógica mediante `is_active`.
