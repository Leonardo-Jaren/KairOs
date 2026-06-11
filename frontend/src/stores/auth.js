import { defineStore } from 'pinia';
import authService from '@/services/auth.service';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    loading: false,
    error: null,
  }),

  getters: {
    // Retorna si el usuario esta autenticado
    isAuthenticated: (state) => !!state.accessToken,
    
    // Retorna si el usuario tiene rol de administrador
    isAdmin: (state) => state.user?.rol === 'admin',
    
    // Retorna si el usuario tiene rol de tecnico
    isTecnico: (state) => state.user?.rol === 'tecnico',
    
    // Retorna si el usuario tiene rol de usuario regular
    isUsuario: (state) => state.user?.rol === 'usuario',
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
      localStorage.removeItem('kairos_user');
      localStorage.removeItem('kairos_access_token');
      localStorage.removeItem('kairos_refresh_token');
    },

    // Establece el estado de la sesion en memoria y en localStorage
    setSession(data) {
      this.accessToken = data.access;
      this.refreshToken = data.refresh;
      this.user = data.usuario;
      
      localStorage.setItem('kairos_user', JSON.stringify(data.usuario));
      localStorage.setItem('kairos_access_token', data.access);
      localStorage.setItem('kairos_refresh_token', data.refresh);
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
        } catch (e) {
          this.logout();
        }
      }
    }
  }
});
