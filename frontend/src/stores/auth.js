import { defineStore } from 'pinia';
import authService from '@/services/auth.service';

// Matriz base de permisos por rol sincronizada con ROL_PERMISOS_BASE del backend
export const ROLE_BASE_PERMISSIONS = {
  superadmin: {
    espacios: { ver: true, crear: true, editar: true, eliminar: true },
    equipos: { ver: true, crear: true, editar: true, eliminar: true },
    mantenimiento: { ver: true, crear: true, editar: true, eliminar: true },
    incidencias: { ver: true, crear: true, editar: true, eliminar: true },
    software: { ver: true, crear: true, editar: true, eliminar: true },
    usuarios: { ver: true, crear: true, editar: true, eliminar: true },
    auditoria: { ver: true, crear: true, editar: true, eliminar: true },
  },
  admin: {
    espacios: { ver: true, crear: true, editar: true, eliminar: true },
    equipos: { ver: true, crear: true, editar: true, eliminar: true },
    mantenimiento: { ver: true, crear: true, editar: true, eliminar: true },
    incidencias: { ver: true, crear: true, editar: true, eliminar: true },
    software: { ver: true, crear: true, editar: true, eliminar: true },
    usuarios: { ver: true, crear: true, editar: true, eliminar: true },
    auditoria: { ver: true, crear: false, editar: false, eliminar: false },
  },
  responsable: {
    espacios: { ver: true, crear: true, editar: true, eliminar: true },
    equipos: { ver: true, crear: true, editar: true, eliminar: false },
    mantenimiento: { ver: true, crear: true, editar: true, eliminar: false },
    incidencias: { ver: true, crear: true, editar: true, eliminar: true },
    software: { ver: true, crear: true, editar: true, eliminar: false },
    usuarios: { ver: true, crear: true, editar: true, eliminar: false },
    auditoria: { ver: true, crear: false, editar: false, eliminar: false },
  },
  tecnico: {
    espacios: { ver: true, crear: false, editar: false, eliminar: false },
    equipos: { ver: true, crear: true, editar: true, eliminar: false },
    mantenimiento: { ver: true, crear: true, editar: true, eliminar: false },
    incidencias: { ver: true, crear: true, editar: true, eliminar: false },
    software: { ver: true, crear: true, editar: true, eliminar: false },
    usuarios: { ver: true, crear: false, editar: false, eliminar: false },
    auditoria: { ver: true, crear: false, editar: false, eliminar: false },
  },
  docente: {
    espacios: { ver: false, crear: false, editar: false, eliminar: false },
    equipos: { ver: false, crear: false, editar: false, eliminar: false },
    mantenimiento: { ver: false, crear: false, editar: false, eliminar: false },
    incidencias: { ver: true, crear: true, editar: false, eliminar: false },
    software: { ver: true, crear: false, editar: false, eliminar: false },
    usuarios: { ver: false, crear: false, editar: false, eliminar: false },
    auditoria: { ver: false, crear: false, editar: false, eliminar: false },
  },
  usuario: {
    espacios: { ver: false, crear: false, editar: false, eliminar: false },
    equipos: { ver: false, crear: false, editar: false, eliminar: false },
    mantenimiento: { ver: false, crear: false, editar: false, eliminar: false },
    incidencias: { ver: true, crear: true, editar: false, eliminar: false },
    software: { ver: true, crear: false, editar: false, eliminar: false },
    usuarios: { ver: false, crear: false, editar: false, eliminar: false },
    auditoria: { ver: false, crear: false, editar: false, eliminar: false },
  },
};

// Variable en modulo para deduplicar peticiones concurrentes a /api/v1/auth/me/
let activeProfilePromise = null;

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    loading: false,
    error: null,
    lastProfileFetchTimestamp: 0,
  }),

  getters: {
    // Retorna si el usuario esta autenticado
    isAuthenticated: (state) => !!state.accessToken,

    // Retorna si el usuario es superadministrador
    isSuperAdmin: (state) => state.user?.rol === 'superadmin' || !!state.user?.is_superuser,

    // Retorna si el usuario tiene rol de administrador
    isAdmin: (state) => state.user?.rol === 'admin',

    // Retorna si el usuario tiene rol de responsable de sede o área
    isResponsable: (state) => state.user?.rol === 'responsable',

    // Retorna si el usuario tiene rol de tecnico
    isTecnico: (state) => state.user?.rol === 'tecnico',

    // Retorna si el usuario tiene rol de docente
    isDocente: (state) => state.user?.rol === 'docente',

    // Retorna si el usuario tiene rol de usuario regular
    isUsuario: (state) => state.user?.rol === 'usuario',

    // Indica si el usuario puede gestionar jerarquías u organigrama
    canManageOrg: (state) => ['superadmin', 'admin', 'responsable'].includes(state.user?.rol),

    // Retorna la lista de sedes asignadas al usuario
    userSedes: (state) => state.user?.sedes || [],

    // Evalúa si el usuario autenticado tiene un permiso específico (por defecto acción 'ver')
    hasPermission: (state) => (modulo, accion = 'ver') => {
      if (!state.user) return false;
      if (state.user.rol === 'superadmin' || state.user.is_superuser) return true;
      if (state.user.permisos_efectivos && state.user.permisos_efectivos[modulo]) {
        return !!state.user.permisos_efectivos[modulo][accion];
      }
      const rolePermissions = ROLE_BASE_PERMISSIONS[state.user.rol];
      if (rolePermissions && rolePermissions[modulo]) {
        return !!rolePermissions[modulo][accion];
      }
      return false;
    },

  },


  actions: {
    // Actualiza el token de acceso despues de un refresco silencioso
    updateAccessToken(token) {
      this.accessToken = token;
      localStorage.setItem('kairos_access_token', token);
    },

    // Realiza el inicio de sesion tradicional con correo y contrasena
    async login(correo, password) {
      this.loading = true;
      this.error = null;
      try {
        const data = await authService.login(correo, password);
        this.setSession(data);
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al iniciar sesion. Por favor intente de nuevo.';
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // Realiza el inicio de sesion federado con Google
    async loginGoogle(token) {
      this.loading = true;
      this.error = null;
      try {
        const data = await authService.loginGoogle(token);
        this.setSession(data);
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al iniciar sesion con Google.';
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // Cierra la sesion del usuario limpiando el estado y el almacenamiento
    logout() {
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      this.error = null;
      this.lastProfileFetchTimestamp = 0;
      activeProfilePromise = null;
      localStorage.removeItem('kairos_user');
      localStorage.removeItem('kairos_access_token');
      localStorage.removeItem('kairos_refresh_token');
    },

    // Establece el estado de la sesion en memoria y en localStorage
    setSession(data) {
      this.accessToken = data.access;
      this.refreshToken = data.refresh;
      this.user = data.usuario;
      this.lastProfileFetchTimestamp = Date.now();
      
      localStorage.setItem('kairos_user', JSON.stringify(data.usuario));
      localStorage.setItem('kairos_access_token', data.access);
      localStorage.setItem('kairos_refresh_token', data.refresh);
    },

    // Consulta al backend para sincronizar el perfil y los permisos efectivos con deduplicacion y control de tasa
    fetchProfile(options = {}) {
      const force = typeof options === 'boolean' ? options : !!options?.force;
      const minIntervalMs = typeof options === 'object' && options?.minIntervalMs !== undefined
        ? options.minIntervalMs
        : 30000;

      if (!this.accessToken) return Promise.resolve(null);

      const now = Date.now();
      if (!force && this.lastProfileFetchTimestamp && (now - this.lastProfileFetchTimestamp < minIntervalMs)) {
        return Promise.resolve(this.user);
      }

      if (activeProfilePromise) {
        return activeProfilePromise;
      }

      activeProfilePromise = (async () => {
        try {
          const data = await authService.getMe();
          if (data) {
            this.user = {
              ...(this.user || {}),
              ...data,
            };
            this.lastProfileFetchTimestamp = Date.now();
            localStorage.setItem('kairos_user', JSON.stringify(this.user));
          }
          return this.user;
        } catch (err) {
          // Registrar marca de tiempo tras fallo para evitar rafagas de reintentos
          this.lastProfileFetchTimestamp = Date.now();
          if (err.response?.status === 401) {
            this.logout();
          }
          return null;
        } finally {
          activeProfilePromise = null;
        }
      })();

      return activeProfilePromise;
    },

    // Intenta restaurar la sesion activa desde localStorage al cargar la aplicacion
    tryAutoLogin() {
      const storedUser = localStorage.getItem('kairos_user');
      const storedAccess = localStorage.getItem('kairos_access_token');
      const storedRefresh = localStorage.getItem('kairos_refresh_token');
      
      if (storedUser && storedAccess && storedRefresh) {
        try {
          this.user = JSON.parse(storedUser);
          this.accessToken = storedAccess;
          this.refreshToken = storedRefresh;
          // Sincronizar en segundo plano para obtener permisos y perfil frescos
          this.fetchProfile();
        } catch (e) {
          this.logout();
        }
      }
    }
  }
});
