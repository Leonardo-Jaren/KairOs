# Lineamientos y Arquitectura Frontend de KairOs (Guía para Agentes y Desarrolladores)

> **Backend y flujo de trabajo (PR, docs, GitHub Projects):** ver [`docs/CONTRIBUCION-IA.md`](docs/CONTRIBUCION-IA.md).  
> **VS Code + Copilot:** ver [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

Este documento define la arquitectura y las reglas de codificación para todo el desarrollo frontend en el proyecto KairOs. Cualquier agente de IA o desarrollador humano debe seguir estrictamente estas pautas para mantener la consistencia, modularidad y escalabilidad del sistema.

---

## 🏗️ 1. Estructura de Directorios y Separación de Responsabilidades

El frontend está construido sobre **Vue 3 (Vite) + Tailwind CSS v4** y se organiza bajo una arquitectura limpia en capas, tratando que se trabaje por componentes y llegar a rondar las 300 lineas de codigo, si sobre pasa es necesario crear mas componentes para una arquitectura limpia:

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

---

## 🚀 5. Flujo de Trabajo Git y Creación Automática de PR

Cuando el usuario indique **"sube los cambios"**, **"crea el PR"**, **"haz el PR"**, **"sube todo"** o similar:
1. **Acción directa y sin redundancia:** No solicitar al usuario que recuerde las directivas de `.github/` o `docs/`; el agente debe asumir y ejecutar todo el ciclo automáticamente.
2. **Revisar cambios y contexto:** Identificar los archivos modificados (`git status`), el módulo afectado y el propósito de los cambios para derivar un `<slug>` descriptivo en kebab-case, el `<modulo>` y un `<HistoriaTitulo>`.
3. **Iniciales y Configuración:** Leer las iniciales del desarrollador desde [`.github/developer-config.json`](.github/developer-config.json) (por defecto `LJ` o el valor configurado).
4. **Convención de Ramas:** Nunca hacer push directamente a `main`. La rama debe cumplir estrictamente con el formato:
   `{ANIO}{Iniciales}_{MesAbrev}{Dia}_{descripcion-kebab}` (ejemplo: `2026LJ_Sep20_actualizar-agents`).
5. **Creación del PR y Proyecto:**
   - Si se tienen cambios pendientes en el árbol de trabajo, moverlos/commitearlos a la rama correspondiente.
   - Ejecutar el script automatizado desde la raíz del proyecto:
     ```powershell
     .\scripts\create-pr-and-project.ps1 -Descripcion "<slug>" -Modulo "<modulo>" -HistoriaTitulo "<titulo>"
     ```
   - O bien, realizar la secuencia de Git (`git checkout -b <rama>`, `git add .`, `git commit -m "..."`, `git push -u origin <rama>`) y crear el Pull Request con `gh pr create` apuntando a `main`, aplicando el contenido y formato de [`.github/pull_request_template.md`](.github/pull_request_template.md).

---

## 6. Lógica de incidencias y mantenimiento

Esta sección es obligatoria para cualquier agente o desarrollador que modifique
incidencias, mantenimientos o equipos.

### 6.1 Modelo de dominio

- Una **incidencia** es una falla o degradación no planificada que afecta o
  puede afectar la disponibilidad de un equipo de cómputo.
- Un reporte crea una incidencia en estado `pendiente`; no crea automáticamente
  una orden de mantenimiento.
- Un **mantenimiento correctivo** es una orden de trabajo que puede originarse
  desde una incidencia. Una incidencia puede tener varios mantenimientos.
- Un **mantenimiento preventivo** es independiente de las incidencias. Si
  durante su ejecución se encuentra una avería, se registra una incidencia
  separada y, si corresponde, una orden correctiva relacionada.
- Una incidencia puede resolverse sin mantenimiento. Un mantenimiento
  correctivo vinculado que termina con `prueba_realizada` y resultado `en_uso`
  cierra automáticamente la incidencia en la misma transacción. Si el equipo
  queda `dañado` o `de_baja`, la incidencia permanece en proceso y sugiere otra
  intervención.

### 6.2 Estados y transiciones

Las incidencias usan `pendiente`, `en_proceso`, `resuelto`, `cerrado`,
`cancelado` y `duplicado`. Solo son válidas estas transiciones:

```text
pendiente -> en_proceso | cancelado | duplicado
en_proceso -> resuelto | cancelado | duplicado
resuelto -> cerrado | en_proceso
```

Resolver exige `resolucion`; cerrar conserva una resolución; cancelar o marcar
como duplicada exige `motivo_cierre`. Una incidencia terminal no se edita. Al
volver de `resuelto` a `en_proceso` se limpia `fecha_resolucion`.

Los mantenimientos usan `pendiente`, `en_proceso`, `resuelto` y `cancelado`:

```text
pendiente -> en_proceso | cancelado
en_proceso -> resuelto | cancelado
```

Una orden resuelta exige `diagnostico`, `trabajo_realizado`,
`prueba_realizada` y un `resultado_equipo` final (`en_uso`, `dañado` o
`de_baja`). `cancelado` no significa que el equipo esté fuera de servicio. El
estado de la orden y el estado operativo del equipo se almacenan por separado.

### 6.3 Equipo, espacio y permisos

- Toda incidencia se registra sobre un equipo vigente y el backend debe
  comprobar que ese equipo pertenece al espacio enviado.
- El espacio conservado en la incidencia es histórico; un traslado posterior
  del equipo no lo cambia.
- `docente` y `usuario` pueden crear incidencias y consultar únicamente las
  propias; no pueden editar, borrar ni cambiar estados.
- `tecnico`, `responsable`, `admin` y `superadmin` realizan triage, asignación,
  cambios de estado, resolución y creación de correctivos dentro de sus
  espacios autorizados.
- La autorización se valida en backend y las vistas frontend deben usar
  permisos efectivos (`hasPermission`), no comparaciones aisladas de roles.
- Se conserva el historial mediante borrado lógico; para una incidencia
  operativa se prefieren `cancelado`, `duplicado` o `cerrado`.

### 6.4 Capas obligatorias y pruebas

La implementación debe respetar:

```text
ViewSet -> Serializer -> Service -> Repository -> Model
```

Las relaciones se exponen mediante `GET /incidencias/{id}/mantenimientos/` y
el correctivo puede crearse con `POST /incidencias/{id}/crear-mantenimiento/`.
Las órdenes se inician con `POST /mantenimiento/{id}/iniciar/` y se finalizan
con `POST /mantenimiento/{id}/finalizar/`; la interfaz no usa el lápiz para
resolver una orden. La finalización funcional cierra automáticamente la
incidencia vinculada y la finalización no funcional conserva la incidencia
abierta para otra intervención.
El payload acepta `incidencia_id` únicamente para correctivos del mismo equipo
y con una incidencia que no esté cerrada, cancelada o duplicada.

Todo cambio en este flujo debe incluir pruebas de autorización, transiciones,
validación equipo-espacio, relación incidencia-mantenimiento y actualización
del estado operativo del equipo, además de la documentación funcional y de API.

