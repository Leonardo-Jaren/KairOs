# Matriz Integral de Módulos y Documentación — KairOs

Índice central que vincula cada módulo funcional con su arquitectura de backend, frontend, base de datos, requerimientos funcionales (RF), requerimientos no funcionales (RNF) e historias de usuario (HU).

---

## 1. Módulos del Sistema

| Módulo | Backend (Apps) | Frontend (Vistas) | Base de Datos (Tablas) | Requerimientos Funcionales | Requerimientos No Funcionales | Historias de Usuario |
|--------|----------------|-------------------|------------------------|----------------------------|-------------------------------|----------------------|
| **Autenticación y Seguridad** | `backend/autenticacion/` | `src/views/auth/` | `usuarios` | [RF-AUTH-001](requerimientos-funcionales/autenticacion-login-sesion.md) | [RNF-AUTH-001](requerimientos-no-funcionales/autenticacion-seguridad-sesion.md) | [HU-AUTH-001](historias-de-usuario/autenticacion-login-sesion.md) |
| **Usuarios y Roles** | `backend/usuarios/` | `src/views/usuarios/` | `usuarios`, `perfil_tecnico` | [RF-USR-001](requerimientos-funcionales/usuarios-gestionar-usuarios.md) | [RNF-USR-001](requerimientos-no-funcionales/usuarios-gestionar-usuarios.md) | [HU-USR-001](historias-de-usuario/usuarios-gestionar-usuarios.md) |
| **Espacios y Campus Tecnológico** | `backend/espacios/` | `src/views/espacios/` | `locales`, `edificios`, `espacios`, `espacios_usuarios` | [RF-ESP-001](requerimientos-funcionales/espacios-gestionar-espacios.md)<br>[RF-ESP-002](requerimientos-funcionales/espacios-plano-interactivo.md)<br>[RF-ESP-003](requerimientos-funcionales/espacios-usuarios-gestionar-asignaciones.md)<br>[RF-ESP-004](requerimientos-funcionales/espacios-mapa-por-locales.md) | [RNF-ESP-001](requerimientos-no-funcionales/espacios-gestionar-espacios.md)<br>[RNF-ESP-002](requerimientos-no-funcionales/espacios-plano-interactivo.md)<br>[RNF-ESP-003](requerimientos-no-funcionales/espacios-usuarios-gestionar-asignaciones.md)<br>[RNF-ESP-004](requerimientos-no-funcionales/espacios-mapa-por-locales.md) | [HU-ESP-001](historias-de-usuario/espacios-gestionar-espacios.md)<br>[HU-ESP-002](historias-de-usuario/espacios-plano-interactivo.md)<br>[HU-ESP-003](historias-de-usuario/espacios-usuarios-gestionar-asignaciones.md)<br>[HU-ESP-004](historias-de-usuario/espacios-mapa-por-locales.md) |
| **Equipos y Hardware** | `backend/equipos/` | `src/views/equipos/` | `equipos`, `componentes` | [RF-EQ-001](requerimientos-funcionales/equipos-gestionar-equipos.md)<br>[RF-EQ-002](requerimientos-funcionales/equipos-componentes-hardware.md)<br>[RF-EQ-003](requerimientos-funcionales/equipos-filtrar-componentes.md) | [RNF-EQ-001](requerimientos-no-funcionales/equipos-gestionar-equipos.md)<br>[RNF-EQ-002](requerimientos-no-funcionales/equipos-componentes-hardware.md)<br>[RNF-EQ-003](requerimientos-no-funcionales/equipos-filtrar-componentes.md) | [HU-EQ-001](historias-de-usuario/equipos-gestionar-equipos.md)<br>[HU-EQ-002](historias-de-usuario/equipos-componentes-hardware.md)<br>[HU-EQ-003](historias-de-usuario/equipos-filtrar-componentes.md) |
| **Software y Licencias** | `backend/software/` | `src/views/software/` | `productos_software`, `software_instalado` | [RF-SW-001](requerimientos-funcionales/software-catalogo-productos.md)<br>[RF-SW-002](requerimientos-funcionales/software-gestionar-instalaciones.md) | [RNF-SW-001](requerimientos-no-funcionales/software-gestionar-software.md) | [HU-SW-001](historias-de-usuario/software-catalogo-productos.md)<br>[HU-SW-002](historias-de-usuario/software-gestionar-instalaciones.md) |
| **Mantenimiento y Soporte** | `backend/mantenimiento/` | `src/views/mantenimiento/` | `mantenimiento`, `tecnico_mantenimiento` | [RF-MANT-001](requerimientos-funcionales/mantenimiento-gestionar-mantenimiento.md) | [RNF-MANT-001](requerimientos-no-funcionales/mantenimiento-gestionar-mantenimiento.md) | [HU-MANT-001](historias-de-usuario/mantenimiento-gestionar-mantenimiento.md) |
| **Incidencias** | `backend/incidencias/` | `src/views/incidencias/` | `incidencias` | [RF-INC-001](requerimientos-funcionales/incidencias-gestionar-incidencias.md) | [RNF-INC-001](requerimientos-no-funcionales/incidencias-gestionar-incidencias.md) | [HU-INC-001](historias-de-usuario/incidencias-gestionar-incidencias.md) |
| **Historial y Auditoría** | `backend/historial/` | `src/views/historial/` | `historial` | [RF-HIST-001](requerimientos-funcionales/historial-auditoria-sistema.md) | [RNF-HIST-001](requerimientos-no-funcionales/historial-auditoria-sistema.md) | [HU-HIST-001](historias-de-usuario/historial-auditoria-sistema.md) |
| **Navegación e Interfaz** | Transversal | `src/layouts/` | N/A | [RF-NAV-001](requerimientos-funcionales/navegacion-colapsar-barra-lateral.md) | [RNF-NAV-001](requerimientos-no-funcionales/navegacion-colapsar-barra-lateral.md) | [HU-NAV-001](historias-de-usuario/navegacion-colapsar-barra-lateral.md) |

---

## 2. Documentos Técnicos Principales

- **Backend:**
  - [Requerimientos y Arquitectura Backend](backend/requerimientos_backend.md)
  - [Catálogo de Endpoints de la API](backend/api_endpoints.md)
- **Frontend:**
  - [Requerimientos y Arquitectura Frontend](frontend/requerimientos_frontend.md)
  - [Mapa de Rutas y Vistas](frontend/rutas_y_vistas.md)
- **Base de Datos:**
  - [Esquema y Modelo Entidad-Relación (Mermaid)](base-de-datos/database_schema.md)
  - [Diccionario de Datos Exhaustivo](base-de-datos/diccionario_de_datos.md)
- **Manual de Usuario:**
  - [Manual de Usuario Paso a Paso con Capturas](manual_usuario/MANUAL_DE_USUARIO.md)
