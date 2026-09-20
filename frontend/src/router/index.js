import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { guestOnly: true },
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/auth/LoginView.vue'),
      },
      {
        path: 'password-reset',
        name: 'PasswordReset',
        component: () => import('@/views/auth/PasswordResetView.vue'),
      },
    ],
  },
  // Redirecciones directas para facilidad de acceso
  {
    path: '/login',
    redirect: '/auth/login',
  },
  {
    path: '/password-reset',
    redirect: '/auth/password-reset',
  },
  {
    path: '/dashboard',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: 'Panel de control' },
      },
      {
        path: '/usuarios',
        name: 'Usuarios',
        component: () => import('@/views/usuarios/UsuariosView.vue'),
        meta: { title: 'Usuarios', modulo: 'usuarios' },
      },
      {
        path: '/espacios',
        name: 'Espacios',
        component: () => import('@/views/espacios/EspaciosView.vue'),
        meta: { title: 'Espacios', modulo: 'espacios' },
      },
      {
        path: '/espacios/usuarios',
        name: 'EspaciosUsuarios',
        component: () => import('@/views/espacios/EspaciosUsuariosView.vue'),
        meta: { title: 'Usuarios por espacio', modulo: 'espacios' },
      },
      {
        path: '/espacios/mapa',
        name: 'CampusTecnologico',
        component: () => import('@/views/espacios/CampusTecnologicoView.vue'),
        meta: { title: 'Mapa tecnológico', modulo: 'espacios' },
      },
      {
        path: '/espacios/:id',
        name: 'EspacioDetalle',
        component: () => import('@/views/espacios/EspacioDetalleView.vue'),
        meta: { title: 'Plano interactivo', modulo: 'espacios' },
      },
      {
        path: '/historial',
        name: 'Historial',
        component: () => import('@/views/historial/HistorialView.vue'),
        meta: { title: 'Historial de auditoría', modulo: 'auditoria' },
      },
      {
        path: '/equipos',
        name: 'Equipos',
        component: () => import('@/views/equipos/EquiposView.vue'),
        meta: { title: 'Equipos', modulo: 'equipos' },
      },
      {
        path: '/componentes',
        name: 'Componentes',
        component: () => import('@/views/equipos/ComponentesView.vue'),
        meta: { title: 'Componentes', modulo: 'equipos' },
      },
      {
        path: '/software',
        name: 'Software',
        component: () => import('@/views/software/SoftwareView.vue'),
        meta: { title: 'Software', modulo: 'software' },
      },
      {
        path: '/software/instalaciones',
        name: 'SoftwareInstalaciones',
        component: () => import('@/views/software/InstalacionesView.vue'),
        meta: { title: 'Instalaciones de software', modulo: 'software' },
      },
      {
        path: '/mantenimiento',
        name: 'Mantenimiento',
        component: () => import('@/views/mantenimiento/MantenimientoView.vue'),
        meta: { title: 'Mantenimiento', modulo: 'mantenimiento' },
      },
      {
        path: '/incidencias',
        name: 'Incidencias',
        component: () => import('@/views/incidencias/IncidenciasView.vue'),
        meta: { title: 'Incidencias', modulo: 'incidencias' },
      },
    ],
  },
  // Ruta comodin para redirigir paginas no encontradas
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    return savedPosition ?? { left: 0, top: 0 };
  },
});

// Guard de navegacion moderno en Vue Router 4 (retornando la ruta de destino)
router.beforeEach((to) => {
  const authStore = useAuthStore();
  
  // Intentar cargar la sesion desde localStorage si no se ha cargado en memoria
  if (!authStore.accessToken) {
    authStore.tryAutoLogin();
  }
  
  const isAuthenticated = authStore.isAuthenticated;

  // 1. Validar si la ruta requiere estar autenticado
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      // Redirigir al inicio de sesion si no esta autenticado
      return { name: 'Login' };
    }
    
    const userRole = authStore.user?.rol;
    const isSuper = userRole === 'superadmin' || authStore.user?.is_superuser;

    // Superadministradores y superusuarios tienen acceso total
    if (isSuper) {
      return true;
    }

    // Validar autorizacion por permisos del modulo (efectivos o plantilla base)
    if (to.meta.modulo) {
      if (!authStore.hasPermission(to.meta.modulo, 'ver')) {
        return { name: 'Dashboard' };
      }
      return true;
    }

    // Validar autorizacion por roles de respaldo si la ruta no tiene modulo asociado
    const allowedRoles = to.meta.roles;
    if (allowedRoles && allowedRoles.length > 0) {
      const hasAccess = allowedRoles.includes(userRole) || (userRole === 'responsable' && allowedRoles.includes('admin'));
      if (!hasAccess) {
        // Redirigir al dashboard si el rol del usuario no tiene permisos
        return { name: 'Dashboard' };
      }
    }
    
    return true;
  } 
  
  // 2. Validar si la ruta es exclusiva para invitados (Login, Recuperacion)
  if (to.matched.some((record) => record.meta.guestOnly)) {
    if (isAuthenticated) {
      // Redirigir al dashboard si ya esta autenticado
      return { name: 'Dashboard' };
    }
    return true;
  } 
  
  // 3. Ruta publica sin restricciones
  return true;
});

export default router;
