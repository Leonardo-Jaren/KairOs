# Mapa de Rutas, Layouts y Vistas — KairOs Frontend

Estructura de navegación definida en `src/router/index.js` y componentes asociados.

---

## 1. Layouts Estructurales

| Layout | Archivo | Propósito | Características |
|--------|---------|-----------|-----------------|
| **AuthLayout** | `src/layouts/AuthLayout.vue` | Contenedor para autenticación y recuperación de credenciales | Fondo limpio con patrón de retícula sutil, tarjeta centrada, pie de página institucional y estado de red seguro. |
| **DashboardLayout** | `src/layouts/DashboardLayout.vue` | Contenedor principal de la aplicación protegida | Barra lateral retráctil con logotipo, indicador de versión, listado de enlaces con iconos Lucide, barra superior con perfil de usuario y botón de cierre de sesión. |

---

## 2. Catálogo de Rutas y Vistas

| Ruta | Nombre de Ruta | Layout | Vista (.vue) | Roles Permitidos | Composable Asociado |
|------|----------------|--------|--------------|------------------|---------------------|
| `/auth/login` | `Login` | AuthLayout | `src/views/auth/LoginView.vue` | Público / Invitado | `useLogin.js` |
| `/auth/password-reset` | `PasswordReset` | AuthLayout | `src/views/auth/PasswordResetView.vue` | Público / Invitado | `usePasswordReset.js` |
| `/dashboard` | `Dashboard` | DashboardLayout | `src/views/dashboard/DashboardView.vue` | Todos (`admin`, `tecnico`, `docente`, `usuario`) | `useDashboard.js` |
| `/usuarios` | `Usuarios` | DashboardLayout | `src/views/usuarios/UsuariosView.vue` | `admin`, `tecnico` | `useUsuarios.js` |
| `/espacios` | `Espacios` | DashboardLayout | `src/views/espacios/EspaciosView.vue` | `admin`, `tecnico` | `useEspacios.js` |
| `/espacios/usuarios` | `EspaciosUsuarios` | DashboardLayout | `src/views/espacios/EspaciosUsuariosView.vue` | `admin`, `tecnico` | `useEspaciosUsuarios.js` |
| `/espacios/mapa` | `CampusTecnologico` | DashboardLayout | `src/views/espacios/CampusTecnologicoView.vue` | `admin`, `tecnico` | `useCampusTecnologico.js` |
| `/espacios/:id` | `EspacioDetalle` | DashboardLayout | `src/views/espacios/EspacioDetalleView.vue` | `admin`, `tecnico` | `usePlanoEspacio.js` |
| `/equipos` | `Equipos` | DashboardLayout | `src/views/equipos/EquiposView.vue` | `admin`, `tecnico` | `useEquipos.js` |
| `/componentes` | `Componentes` | DashboardLayout | `src/views/equipos/ComponentesView.vue` | `admin`, `tecnico` | `useComponentes.js` |
| `/software` | `Software` | DashboardLayout | `src/views/software/SoftwareView.vue` | `admin`, `tecnico`, `docente` | `useSoftware.js` |
| `/software/instalaciones` | `SoftwareInstalaciones` | DashboardLayout | `src/views/software/InstalacionesView.vue` | `admin`, `tecnico`, `docente` | `useInstalaciones.js` |
| `/mantenimiento` | `Mantenimiento` | DashboardLayout | `src/views/mantenimiento/MantenimientoView.vue` | `admin`, `tecnico` | `useMantenimiento.js` |
| `/incidencias` | `Incidencias` | DashboardLayout | `src/views/incidencias/IncidenciasView.vue` | `admin`, `tecnico`, `docente` | `useIncidencias.js` |
| `/historial` | `Historial` | DashboardLayout | `src/views/historial/HistorialView.vue` | `admin`, `tecnico` | `useHistorial.js` |

---

## 3. Detalle de Módulos y Funcionalidades en Vistas

### 3.1 Vista de Campus Tecnológico (`/espacios/mapa`)
- **Descripción:** Visualizador gráfico del campus institucional y croquis de cada piso en edificios/pabellones.
- **Interacciones:**
  - Selector desplegable o tarjetas de edificios (Pabellón 1, 2, 3, etc.).
  - Pestañas de niveles de piso (Piso 1, Piso 2, etc.).
  - Renderizado dinámico del croquis vectorial o reticular (`CroquisPiso.vue`) mostrando aulas, laboratorios y pasillos con estado de operatividad en tiempo real.
  - Al hacer clic en un laboratorio, navega de inmediato a su vista de plano interactivo (`/espacios/:id`).

### 3.2 Vista de Plano Interactivo de Espacio (`/espacios/:id`)
- **Descripción:** Representación en cuadrícula visual de los puestos de trabajo de un laboratorio específico.
- **Interacciones:**
  - Cada celda de la retícula representa una terminal o estación física.
  - Los puestos tienen colores distintivos según el estado del equipo asignado (Verde: En uso, Amarillo: En mantenimiento, Rojo: Dañado, Gris: Vacío).
  - Al seleccionar un puesto, un panel lateral despliega la ficha del equipo (código, marca, IP, MAC y software instalado).
  - Los administradores y técnicos pueden reubicar equipos arrastrando o seleccionando una nueva coordenada y persistir el cambio con `/api/v1/espacios/{id}/disposicion/`.

### 3.3 Vista de Tablero de Mantenimiento (`/mantenimiento`)
- **Descripción:** Gestión de ciclo de vida de órdenes de servicio técnico preventivo y correctivo.
- **Interacciones:**
  - Filtros rápidos por estado (`pendiente`, `en_proceso`, `resuelto`, `cancelado`).
  - Modal para registro de nuevo mantenimiento con selección asistida de equipos y técnicos disponibles.
  - Transición fluida de estados y registro automático en el log de auditoría.
