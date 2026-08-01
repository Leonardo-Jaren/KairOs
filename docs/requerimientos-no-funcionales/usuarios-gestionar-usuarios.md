# RNF-USUARIOS-001: Seguridad y mantenibilidad de usuarios

| Campo | Valor |
|-------|-------|
| Módulo | Usuarios |
| Categoría | Seguridad / Mantenibilidad |
| Fecha | 2026-08-01 |
| Autor | Leonardo Jaren |
| Estado | En revisión |

## Descripción

La administración de usuarios debe proteger credenciales, aplicar autorización por rol y mantener separadas las responsabilidades de acceso a datos, negocio y transporte HTTP.

## Justificación

Las cuentas controlan el acceso a KairOs. Una filtración de contraseña, un escalamiento de rol o una eliminación física podrían comprometer la operación y la trazabilidad institucional.

## Métrica / umbral

| Métrica | Valor objetivo |
|---------|----------------|
| Exposición de contraseñas en respuestas | 0 campos sensibles |
| Operaciones protegidas sin autenticación | 100 % rechazadas |
| Cobertura funcional automatizada | Repository, service, permisos y API verificados |
| Tamaño de página predeterminado | 10 registros, máximo 100 |

## Implementación esperada

- JWT adjunto mediante el cliente Axios común.
- Hashing mediante los métodos seguros del modelo de usuario.
- ORM restringido a `UsuarioRepository`.
- Reglas de permisos y unicidad en `UsuarioService`.
- Componentes y composable reutilizables en frontend.

## Verificación

- [x] Ejecutar `python manage.py test usuarios autenticacion`.
- [x] Ejecutar las pruebas Vitest de `useUsuarios`.
- [x] Revisar que el serializer de salida no declare `password`.

## Relación con RF

- RF relacionados: RF-USUARIOS-001

## Notas

La paleta del frontend se centraliza en `frontend/src/style.css` mediante `@theme` de Tailwind CSS v4.
