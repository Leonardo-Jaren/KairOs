# RNF-AUTH-001: Seguridad, Integridad y Resiliencia en Autenticación

| Campo | Valor |
|-------|-------|
| Modulo | Autenticación |
| Categoria | Seguridad |
| Fecha | 2026-09-14 |
| Autor | Equipo KairOs |
| Estado | Aprobado |

## Descripcion

El subsistema de autenticación debe garantizar la confidencialidad de las credenciales, la validez criptográfica de las sesiones y la protección contra ataques de fuerza bruta, secuestro de sesión y suplantación de identidad en entornos de red institucional.

## Justificacion

Dado que KairOs gestiona la infraestructura física, inventario y configuración de redes de laboratorios de cómputo, una brecha en la autenticación comprometería la operatividad del campus tecnológico.

## Metrica / umbral

| Metrica | Valor objetivo |
|---------|----------------|
| Tiempo de vida de Access Token | Máximo 60 minutos |
| Tiempo de vida de Refresh Token | Máximo 7 días con rotación obligatoria |
| Latencia en emisión de JWT | < 250 ms |
| Latencia de validación Google SSO | < 800 ms (sujeto a red externa) |
| Algoritmo de firma de tokens | HMAC-SHA256 (HS256) |

## Implementacion esperada

- Firma de tokens JWT mediante clave privada en entorno restringido (`SIMPLE_JWT_SECRET_KEY`).
- Encolamiento y deduplicación de peticiones de refresco concurrentes en Axios para evitar *race conditions*.
- Validación estricta del `aud` (Client ID) en tokens de Google Identity.
- Cifrado seguro de contraseñas locales mediante hash con sal (*salt*) de Django.

## Verificacion

- [x] Pruebas unitarias de emisión y rechazo de tokens en `backend/autenticacion/tests.py`.
- [x] Pruebas de interceptores y silent refresh en `frontend/src/services/api.js`.
- [x] Suite automatizada de tests de LoginView y Google Identity Service en Vitest.

## Relacion con RF

- RF relacionados: RF-AUTH-001 (Autenticación y Sesiones).

## Notas

Cumple con las directivas de seguridad del marco OWASP Top 10 para APIs REST.
