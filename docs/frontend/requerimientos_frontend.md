# Requerimientos y Arquitectura del Frontend — KairOs

Frontend SPA para la Administración Integral de Campus Tecnológico, Laboratorios e Infraestructura.

---

## 1. Visión General del Frontend

El frontend de **KairOs** está construido con **Vue 3** bajo el paradigma de **Composition API** (`<script setup>`), empaquetado ultra-rápido con **Vite**, estilos de última generación con **Tailwind CSS v4** y gestión de estado reactivo con **Pinia**.

### 1.1 Principios de Diseño y Arquitectura
- **Vistas Delgadas (Thin Views):** Los archivos `.vue` en `src/views/` únicamente contienen el marcado HTML y estilos. Toda la reactividad, llamadas a servicios, validaciones y lógica de estado residen en composables dedicados dentro de `src/composables/`.
- **Diseño sin `tailwind.config.js`:** Al usar Tailwind CSS v4, el sistema de diseño corporativo se declara en `src/style.css` mediante la directiva `@theme`.
- **Servicios API Desacoplados (SRP):** Cada dominio de datos tiene su propio archivo de servicio en `src/services/` (ej. `equipos.service.js`), consumiendo el cliente central `api.js`.
- **Iconografía Unificada:** Se emplea exclusivamente la librería oficial `@lucide/vue` con grosor de línea coherente, evitando SVGs duplicados.
- **Alias de Ruta `@`:** Toda importación interna utiliza el alias `@` para referenciar `src/`, prohibiendo rutas relativas multinivel (`../../`).

---

## 2. Stack Tecnológico Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Vue 3** | ^3.5.34 | Framework reactivo con Composition API |
| **Vite** | ^8.0.12 | Servidor de desarrollo HMR y compilador de producción |
| **Tailwind CSS v4** | ^4.3.0 | Framework de estilos utilitarios basado en CSS nativo |
| **Pinia** | ^3.0.4 | Store global para autenticación y estado reactivo |
| **Vue Router** | ^5.1.0 (Router 4/5 API) | Enrutamiento del lado del cliente con guards y RBAC |
| **Axios** | ^1.16.1 | Cliente HTTP para consumo de endpoints REST con interceptores |
| **Lucide Vue** | ^1.17.0 / `lucide-vue-next` | Conjunto oficial de iconos de interfaz |
| **Vitest** | ^4.1.10 | Framework de pruebas unitarias y de componentes |
| **Vue Test Utils** | ^2.4.11 | Utilitarios de montaje y aserción de componentes |

---

## 3. Estructura de Directorios (`src/`)

```
frontend/src/
├── assets/                 # Recursos estáticos (logos institucionales, imágenes)
├── components/             # Componentes UI reutilizables organizados por tipo:
│   ├── buttons/            # BaseButton.vue, botones con estados de carga y variantes
│   ├── inputs/             # BaseInput.vue con soporte para validaciones e iconos
│   ├── selects/            # BaseSelect.vue, BasePaginatedSelect.vue
│   ├── tables/             # BaseTable.vue con cabeceras ordenables y slots
│   ├── pagination/         # BasePagination.vue con controles de página
│   ├── modals/             # BaseModal.vue accesible con transiciones
│   ├── toasts/             # BaseToast.vue para notificaciones no intrusivas
│   └── espacios/           # CroquisPiso.vue, componentes del mapa interactivo
├── composables/            # Lógica de negocio extraída por módulos funcionales:
│   ├── auth/               # useLogin.js, usePasswordReset.js
│   ├── dashboard/          # useDashboard.js
│   ├── usuarios/           # useUsuarios.js
│   ├── espacios/           # useEspacios.js, usePlanoEspacio.js, useCampusTecnologico.js
│   ├── equipos/            # useEquipos.js, useComponentes.js
│   ├── software/           # useSoftware.js, useInstalaciones.js
│   ├── mantenimiento/      # useMantenimiento.js
│   ├── incidencias/        # useIncidencias.js
│   ├── historial/          # useHistorial.js
│   └── shared/             # useAutoFilters.js, usePagination.js
├── layouts/                # Layouts estructurales (AuthLayout.vue, DashboardLayout.vue)
├── router/                 # Configuración de rutas y guards de navegación
├── services/               # Clientes de API con Axios divididos por entidad
├── stores/                 # Stores reactivos de Pinia (auth.js)
├── utils/                  # Helpers de validación de red (IP/MAC), formateadores
└── views/                  # Vistas de páginas por módulo funcional
```

---

## 4. Gestión de Estado y Ciclo de Autenticación

### 4.1 Store de Autenticación (`useAuthStore`)
Ubicado en `src/stores/auth.js`:
- Mantiene en memoria y sincroniza en `localStorage`:
  - `accessToken` (JWT de corta duración).
  - `refreshToken` (JWT de larga duración).
  - `user`: Objeto con perfil del usuario (`id`, `nombre`, `correo`, `rol`).
- Métodos principales:
  - `login(credentials)`: Envía petición a `/api/v1/auth/login/` y almacena tokens.
  - `loginWithGoogle(idToken)`: Autentica mediante Google Identity Services.
  - `updateAccessToken(newToken)`: Actualiza el access token recibido tras renovación.
  - `logout()`: Purga tokens de memoria y almacenamiento, redirigiendo a login.
  - `tryAutoLogin()`: Restaura la sesión al refrescar la página.

### 4.2 Interceptor de Axios y Silent Refresh Automático
Configurado en `src/services/api.js`:
1. **Interceptor de Petición:** Inyecta automáticamente el token de acceso en la cabecera `Authorization: Bearer <token>`.
2. **Interceptor de Respuesta (Manejo de 401 Unauthorized):**
   - Cuando el access token expira, el backend responde con código HTTP 401.
   - El interceptor detecta el 401 y encola las peticiones concurrentes (`failedQueue`).
   - Envía automáticamente una petición al endpoint `/api/v1/auth/refresh/` con el `refresh_token`.
   - Al obtener un nuevo access token, lo persiste en el store y reintenta la petición original sin que el usuario experimente desconexión ni recarga de página.
   - Si el refresh token también ha expirado, cierra la sesión y redirige formalmente a `/login`.

---

## 5. Control de Navegación y Permisos de Ruta (Navigation Guards)

El guard global `router.beforeEach` en `src/router/index.js` evalúa en cada cambio de vista:
1. **Rutas Protegidas (`requiresAuth: true`):**
   - Si no existe sesión activa, redirige inmediatamente a `/login`.
   - Si la ruta define roles permitidos (`meta.roles`), verifica que `authStore.user.rol` esté incluido (ej. `roles: ['admin', 'tecnico']`). En caso contrario, redirige al Dashboard impidiendo accesos indebidos.
2. **Rutas de Invitado (`guestOnly: true`):**
   - Si el usuario ya está autenticado e intenta acceder a `/login` o `/password-reset`, se le redirige automáticamente a `/dashboard`.

---

## 6. Sistema de Diseño con Tailwind CSS v4

La personalización corporativa se define centralmente en `src/style.css`:

```css
@import "tailwindcss";

@theme {
  --color-kairos-blue: #2563EB;
  --color-kairos-blue-hover: #1D4ED8;
  --color-kairos-navy: #0F172A;
  --color-kairos-navy-light: #1E293B;
  --color-kairos-gray-bg: #F8FAFC;
  --color-kairos-border: #E2E8F0;
  
  --font-sans: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}
```

- Se aplican micro-animaciones en hover, focus y transiciones suaves (`transition-all duration-200`) para garantizar una interacción fluida y moderna.
