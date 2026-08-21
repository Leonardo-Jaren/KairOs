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
        meta: { title: 'Usuarios', roles: ['admin', 'tecnico'] },
      },
      {
        path: '/espacios',
        name: 'Espacios',
        component: () => import('@/views/espacios/EspaciosView.vue'),
        meta: { title: 'Espacios', roles: ['admin', 'tecnico'] },
      },
      {
        path: '/espacios/usuarios',
        name: 'EspaciosUsuarios',
        component: () => import('@/views/espacios/EspaciosUsuariosView.vue'),
        meta: { title: 'Usuarios por espacio', roles: ['admin', 'tecnico'] },
      },
      {
        path: '/espacios/mapa',
        name: 'CampusTecnologico',
        component: () => import('@/views/espacios/CampusTecnologicoView.vue'),
        meta: { title: 'Mapa tecnológico', roles: ['admin', 'tecnico'] },
      },
      {
        path: '/espacios/:id',
        name: 'EspacioDetalle',
        component: () => import('@/views/espacios/EspacioDetalleView.vue'),
        meta: { title: 'Plano interactivo', roles: ['admin', 'tecnico'] },
      },
      {
        path: '/historial',
        name: 'Historial',
        component: () => import('@/views/historial/HistorialView.vue'),
        meta: { title: 'Historial de auditoría', roles: ['admin', 'tecnico'] },
      },
      {
        path: '/equipos',
        name: 'Equipos',
        component: () => import('@/views/equipos/EquiposView.vue'),
        meta: { title: 'Equipos', roles: ['admin', 'tecnico'] },
      },
      {
        path: '/componentes',
        name: 'Componentes',
        component: () => import('@/views/equipos/ComponentesView.vue'),
        meta: { title: 'Componentes', roles: ['admin', 'tecnico'] },
      },
      {
        path: '/software',
        name: 'Software',
        component: () => import('@/views/software/SoftwareView.vue'),
        meta: { title: 'Software', roles: ['admin', 'tecnico', 'docente'] },
      },
      {
        path: '/software/instalaciones',
        name: 'SoftwareInstalaciones',
        component: () => import('@/views/software/InstalacionesView.vue'),
        meta: { title: 'Instalaciones de software', roles: ['admin', 'tecnico', 'docente'] },
      },
      {
        path: '/mantenimiento',
        name: 'Mantenimiento',
        component: () => import('@/views/mantenimiento/MantenimientoView.vue'),
        meta: { title: 'Mantenimiento', roles: ['admin', 'tecnico'] },
      },
      {
        path: '/incidencias',
        name: 'Incidencias',
        component: () => import('@/views/incidencias/IncidenciasView.vue'),
        meta: { title: 'Incidencias', roles: ['admin', 'tecnico', 'docente'] },
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
    
    // Validar autorizacion por roles si la ruta los especifica
    const allowedRoles = to.meta.roles;
    if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(authStore.user?.rol)) {
      // Redirigir al dashboard si el rol del usuario no tiene permisos
      return { name: 'Dashboard' };
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
