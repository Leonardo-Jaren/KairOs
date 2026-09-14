# HU-AUTH-001: Iniciar Sesión con Credenciales y Google SSO

| Campo | Valor |
|-------|-------|
| Modulo | Autenticación |
| Prioridad | Alta |
| Fecha | 2026-09-14 |
| Autor | Equipo KairOs |
| Estado | Hecho |

## Historia

**Como** usuario del sistema (administrador, técnico o docente)  
**Quiero** autenticarme en la plataforma KairOs usando mi correo y contraseña o mi cuenta institucional de Google  
**Para** acceder de manera segura a las herramientas de administración y consulta de infraestructura tecnológica.

## Descripcion

El acceso al sistema requiere una autenticación ágil y segura. Los usuarios disponen de dos modalidades:
1. Acceso tradicional con correo electrónico y contraseña cifrada.
2. Acceso federado en un solo clic mediante Google Identity Services (SSO institucional).

Al autenticarse exitosamente, el usuario recibe un par de tokens JWT que gestionan la sesión y renuevan el acceso sin interrupciones durante el trabajo diario.

## Criterios de aceptacion

- [x] **Dado** un usuario registrado con credenciales válidas, **cuando** ingresa correo y clave y presiona "Ingresar al Sistema", **entonces** el sistema emite los tokens JWT y lo redirige al Dashboard.
- [x] **Dado** un usuario que selecciona "Continuar con Google", **cuando** completa el diálogo de Google One Tap / SSO, **entonces** el backend valida el ID Token externamente y abre la sesión correspondiente.
- [x] **Dado** un usuario con credenciales incorrectas, **cuando** intenta iniciar sesión, **entonces** el sistema muestra un mensaje claro de error sin revelar si el correo existe.
- [x] **Dado** un usuario desactivado, **cuando** intenta acceder, **entonces** el sistema bloquea el ingreso indicando que la cuenta se encuentra suspendida.

## Alcance tecnico

| Capa | Archivos / endpoints |
|------|----------------------|
| API | `POST /api/v1/auth/login/`, `POST /api/v1/auth/google/` |
| Service | `backend/autenticacion/services/` |
| Frontend Store | `frontend/src/stores/auth.js` |
| Frontend View | `frontend/src/views/auth/LoginView.vue` |

## RF / RNF relacionados

- RF: RF-AUTH-001 (Autenticación y Sesiones)
- RNF: RNF-AUTH-001 (Seguridad y Resiliencia en Autenticación)

## Notas de implementacion

Implementado con Axios interceptors para silent refresh (401), Pinia para reactividad global y validaciones en tiempo real con BaseInput.
