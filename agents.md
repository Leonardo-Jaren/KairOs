# Lineamientos y Arquitectura Frontend de KairOs (Guía para Agentes y Desarrolladores)

> **Backend y flujo de trabajo (PR, docs, GitHub Projects):** ver [`docs/CONTRIBUCION-IA.md`](docs/CONTRIBUCION-IA.md).  
> **VS Code + Copilot:** ver [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

Este documento define la arquitectura y las reglas de codificación para todo el desarrollo frontend en el proyecto KairOs. Cualquier agente de IA o desarrollador humano debe seguir estrictamente estas pautas para mantener la consistencia, modularidad y escalabilidad del sistema.

---

## 🏗️ 1. Estructura de Directorios y Separación de Responsabilidades

El frontend está construido sobre **Vue 3 (Vite) + Tailwind CSS v4** y se organiza bajo una arquitectura limpia en capas:

### Carpetas Principales (`src/`)
*   **`src/components/`**: Los componentes de la interfaz de usuario se agrupan en subcarpetas específicas según su categoría o tipo de control (p. ej., `buttons/`, `inputs/`, `tables/`, `selects/`, `toasts/`, `icons/`).
*   **`src/layouts/`**: Contenedores estructurales reutilizables (p. ej., `AuthLayout.vue`, `DashboardLayout.vue`).
*   **`src/composables/`**: Lógica de negocio de la vista extraída. Ningún script en una vista debe volverse extenso.
*   **`src/services/`**: Módulos de peticiones HTTP con Axios, organizados y divididos por su dominio/modelo idénticamente al backend (p. ej., `auth.service.js`, `usuarios.service.js`, `equipos.service.js`).
*   **`src/stores/`**: Manejo de estado reactivo global con Pinia.
*   **`src/views/`**: Componentes de página estructurados por módulos funcionales (p. ej., `auth/`, `dashboard/`, `equipos/`).

---

## 🎨 2. Configuración de Diseño y Estilos con Tailwind CSS v4

*   **Sin `tailwind.config.js`:** Al usar Tailwind CSS v4, toda la personalización de temas se realiza directamente dentro del archivo global de estilos `src/style.css` utilizando la directiva `@theme`.
*   **Reusabilidad de Colores:** Los colores corporativos (p. ej., `kairos-blue`, `kairos-navy`, `kairos-navy-light`) se definen como variables CSS dentro de `@theme` y se aplican usando clases de utilidad de Tailwind en todo el proyecto.
*   **Micro-animaciones:** Añadir transiciones suaves en todos los elementos interactivos (hover, active, focus) para asegurar una experiencia de usuario premium y fluida.

---

## 🧪 3. Reglas de Codificación y Mejores Prácticas

### 3.1. Vistas Delgadas y Lógica en Composables
*   Las vistas (`.vue` en `src/views/`) deben enfocarse en la plantilla (HTML) y la presentación (estilos).
*   **Regla de Oro:** Todo el estado reactivo, métodos, validaciones y llamadas a servicios de la vista deben extraerse a un archivo **Composable** dentro de `src/composables/[modulo]/use[Nombre].js` (p. ej., `src/composables/auth/useLogin.js`).
*   El archivo de la vista simplemente importa el composable y expone sus variables y funciones al template.

### 3.2. Importaciones con Alias de Ruta `@`
*   **Evitar rutas relativas largas:** Queda estrictamente prohibido utilizar rutas relativas con múltiples niveles (p. ej. `../../stores/auth` o `../../../components/inputs/BaseInput.vue`).
*   **Uso del alias `@`:** En su lugar, se debe utilizar el alias `@` configurado en Vite que apunta a la carpeta `src/` (p. ej. `@/stores/auth`, `@/components/inputs/BaseInput.vue`). Esto previene fallos de resolución en el servidor de desarrollo y producción.

### 3.3. Iconografía Consistente con Lucide
*   **Biblioteca Oficial:** Todos los iconos de la interfaz de usuario deben ser importados directamente desde la biblioteca oficial `@lucide/vue` (p. ej. `import { User, Lock } from '@lucide/vue'`).
*   **Evitar SVG duplicados:** Evitar escribir SVGs inline repetitivos para iconos estándar del sistema, con el fin de simplificar el marcado HTML y asegurar que todos los iconos mantengan el mismo grosor de línea (`stroke-width`) y comportamiento interactivo.

### 3.4. Modularidad de Componentes
*   Evitar agrupar todos los componentes dentro de una única carpeta plana.
*   Dividir por propósito:
    *   `src/components/inputs/BaseInput.vue`
    *   `src/components/buttons/BaseButton.vue`
    *   `src/components/tables/BaseTable.vue`
    *   `src/components/selects/BaseSelect.vue`
*   Cada componente debe ser parametrizado con `props`, eventos (`emits`) y ranuras (`slots`) para facilitar su reutilización en otros módulos.

### 3.5. Servicios API Modulares (SRP)
*   **`src/services/api.js`**: Cliente base de Axios. Contiene la configuración global, interceptores para adjuntar cabeceras JWT (`Authorization`) e interceptores de respuesta para manejar silent refresh de tokens (401 Unauthorized).
*   **Servicios por Entidad**: Dividir los métodos en archivos de servicio específicos de dominio que imiten el backend:
    *   `auth.service.js`: Login tradicional, inicio de sesión de Google, restablecimiento de contraseña.
    *   `usuarios.service.js`: CRUD de usuarios.
    *   `equipos.service.js`: CRUD de hardware y componentes.
    *   `espacios.service.js`: Ubicaciones y pabellones.

### 3.6. Estilo de Comentarios
*   **Sin emojis ni iconos:** Los comentarios de código deben ser sencillos, claros y redactados en español.
*   **Formato de comentarios:** Usar comentarios descriptivos simples de una o varias líneas para explicar lógica compleja, pero evitando elementos ornamentales.
    *   *Correcto:* `// Valida que el formato del correo electronico sea correcto`
    *   *Incorrecto:* `// 🚀 Valida que el formato del correo sea correcto ✨`

---

## 🔒 4. Seguridad en Navegación y Consumo de API

*   **Guard de Rutas:** Configurar el `beforeEach` de Vue Router para interceptar la navegación hacia rutas que requieran autenticación (`meta.requiresAuth`).
*   **Verificación de Roles:** Validar que el rol almacenado en el Pinia Store coincida con los roles autorizados en la ruta (`meta.roles`) antes de permitir el acceso.
*   **Silent Refresh Interceptor:** Implementar la renovación automática del token de acceso (`access`) usando el token de refresco (`refresh`) ante respuestas HTTP 401 del backend, sin interrumpir la sesión activa del usuario.
