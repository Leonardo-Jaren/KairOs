# RF-AUTH-001: Autenticación, Inicio de Sesión y Gestión de Sesiones

| Campo | Valor |
|-------|-------|
| Modulo | Autenticación |
| Version | 1.0 |
| Fecha | 2026-09-14 |
| Autor | Equipo KairOs |
| Estado | Aprobado |

## Descripcion

El sistema debe proveer mecanismos seguros de autenticación para los usuarios de la plataforma KairOs mediante credenciales locales (correo institucional y contraseña cifrada con algoritmo seguro) y autenticación federada con Google Identity Services (SSO institucional). La sesión se mantiene mediante tokens JWT (Access Token y Refresh Token) con renovación silenciosa sin interrumpir el trabajo del usuario.

## Actores

- Administrador
- Técnico
- Docente
- Usuario institucional

## Precondiciones

- El usuario debe estar registrado en la base de datos institucional.
- La cuenta del usuario debe tener el estado activo (`is_active = True`).

## Flujo principal

1. El usuario accede a la pantalla de inicio de sesión (`/auth/login`).
2. El usuario introduce su correo institucional y su contraseña, o hace clic en "Continuar con Google".
3. El sistema valida las credenciales o verifica la firma y vigencia del ID Token de Google ante los servidores de Google.
4. El sistema emite un par de tokens JWT:
   - `access`: Token de acceso firmado con vigencia de 1 hora.
   - `refresh`: Token de actualización firmado con vigencia de 7 días.
5. El frontend almacena los tokens en el store reactivo de Pinia y persiste en almacenamiento seguro.
6. El usuario es redirigido a la vista de `/dashboard`.

## Flujos alternos / excepciones

| Caso | Comportamiento esperado |
|------|-------------------------|
| Credenciales inválidas | Retorna HTTP 401 con mensaje: "Credenciales inválidas. Por favor verifique el correo electrónico y la contraseña." |
| Usuario desactivado (`is_active=False`) | Retorna HTTP 403 con mensaje: "Su cuenta de usuario está desactivada. Comuníquese con el administrador." |
| Expiración de Access Token durante la navegación | El interceptor de Axios captura la respuesta 401, envía el Refresh Token a `/api/v1/auth/refresh/`, recibe un nuevo Access Token y reintenta la petición original transparentemente. |
| Expiración de Refresh Token | El interceptor redirige forzosamente al usuario a `/login` limpiando la memoria. |
| Token de Google inválido o vencido | Retorna HTTP 400 Bad Request indicando el fallo en la verificación del token de identidad. |

## Reglas de negocio

- El correo electrónico institucional es el identificador único (`USERNAME_FIELD = 'correo'`).
- Las contraseñas locales se almacenan aplicando hash criptográfico mediante PBKDF2/Argon2.
- La rotación de tokens (`ROTATE_REFRESH_TOKENS`) está activa en el backend.
- Las rutas protegidas validan el rol del usuario contra las directivas de autorización antes de renderizar la vista.

## Criterios de aceptacion

- [x] Permite autenticación con correo institucional y contraseña local.
- [x] Permite autenticación federada con botón Google One Tap / SSO.
- [x] Genera y renueva tokens JWT automáticamente sin cerrar la sesión durante operaciones válidas.
- [x] Bloquea el acceso a cuentas con `is_active = False`.

## Endpoints / componentes relacionados

| Tipo | Ruta / archivo |
|------|----------------|
| API Login Local | `POST /api/v1/auth/login/` |
| API Login Google | `POST /api/v1/auth/google/` |
| API Token Refresh | `POST /api/v1/auth/refresh/` |
| Backend | `backend/autenticacion/` |
| Frontend Store | `frontend/src/stores/auth.js` |
| Frontend Vista | `frontend/src/views/auth/LoginView.vue` |

## Notas

Cumple con las directivas de seguridad JWT y RBAC descritas en la arquitectura general de KairOs.
