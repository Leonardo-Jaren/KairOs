import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

// Crear instancia central de Axios apuntando al backend
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de peticion para adjuntar el JWT token de acceso
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;
    
    // Si existe el token de acceso lo agregamos en la cabecera Authorization
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Variable para controlar peticiones de refresco en cola y evitar bucles
let isRefreshing = false;
let failedQueue = [];

// Procesa la cola de peticiones retenidas mientras se refrescaba el token
const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Interceptor de respuesta para gestionar errores de autenticacion (401)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Verificar si el servidor respondio con 401 Unauthorized y no se ha reintentado la peticion
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      const authStore = useAuthStore();
      
      // Si ya se esta realizando el refresco de token, encolamos la peticion actual
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }
      
      // Marcar peticion original para evitar reintentarla indefinidamente
      originalRequest._retry = true;
      isRefreshing = true;
      
      const refreshToken = authStore.refreshToken;
      
      // Si no tenemos refresh token, desautenticar directamente
      if (!refreshToken) {
        isRefreshing = false;
        authStore.logout();
        router.push('/login');
        return Promise.reject(error);
      }
      
      try {
        // Enviar peticion directa al endpoint de refresco utilizando axios base
        const response = await axios.post('http://localhost:8000/api/v1/auth/refresh/', {
          refresh: refreshToken,
        });
        
        const newAccessToken = response.data.access;
        
        // Actualizar el token en el store global y en el almacenamiento local
        authStore.updateAccessToken(newAccessToken);
        
        // Procesar las peticiones en cola con el nuevo token
        processQueue(null, newAccessToken);
        isRefreshing = false;
        
        // Reintentar la peticion original con la cabecera actualizada
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Si el refresco tambien falla, limpiar sesion y redirigir al login
        processQueue(refreshError, null);
        isRefreshing = false;
        authStore.logout();
        router.push('/login');
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
