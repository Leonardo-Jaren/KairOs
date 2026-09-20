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

// Helper para decodificar el payload de un token JWT
const decodeJwtPayload = (token) => {
  try {
    if (!token || typeof token !== 'string') return null;
    const parts = token.split('.');
    if (parts.length < 2) return null;
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
};

// Evalua si un token JWT ha expirado o esta a punto de expirar
const isTokenExpired = (token, thresholdSeconds = 15) => {
  const payload = decodeJwtPayload(token);
  if (!payload || !payload.exp) return false;
  return Date.now() >= (payload.exp - thresholdSeconds) * 1000;
};

// Verifica si la URL es un endpoint publico de autenticacion
const isPublicEndpoint = (url = '') => {
  return url.includes('/auth/login') ||
         url.includes('/auth/refresh') ||
         url.includes('/auth/password-reset') ||
         url.includes('/auth/google');
};

// Mapa para deduplicar peticiones GET identicas en vuelo
const inFlightGetRequests = new Map();

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

// Interceptor de peticion para adjuntar el JWT token de acceso y refrescar proactivamente si expiro
api.interceptors.request.use(
  async (config) => {
    const authStore = useAuthStore();
    let token = authStore.accessToken;
    const url = config.url || '';

    // Si el token ha expirado y contamos con refreshToken, refrescar proactivamente
    // antes de enviar la solicitud para evitar generar 401s innecesarios en el backend
    if (token && isTokenExpired(token) && authStore.refreshToken) {
      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const response = await axios.post('http://localhost:8000/api/v1/auth/refresh/', {
            refresh: authStore.refreshToken,
          });
          const newToken = response.data.access;
          authStore.updateAccessToken(newToken);
          processQueue(null, newToken);
          token = newToken;
        } catch (refreshErr) {
          processQueue(refreshErr, null);
          authStore.logout();
          router.push('/login');
          return Promise.reject(refreshErr);
        } finally {
          isRefreshing = false;
        }
      } else {
        token = await new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        });
      }
    }

    // Si existe token, adjuntarlo en la cabecera Authorization
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

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

    // Si el servidor respondió con 403 Forbidden, sincronizar permisos en segundo plano
    // (salvo que la petición rechazada sea el propio perfil para evitar bucles infinitos)
    if (error.response && error.response.status === 403) {
      const failedUrl = error.config?.url || '';
      const isMeRequest = failedUrl.includes('/auth/me');
      const authStore = useAuthStore();

      if (isMeRequest) {
        authStore.logout();
        router.push('/login');
      } else {
        authStore.fetchProfile({ minIntervalMs: 5000 }).then(() => {
          const currentModulo = router.currentRoute.value?.meta?.modulo;
          if (currentModulo && !authStore.hasPermission(currentModulo, 'ver')) {
            router.push('/dashboard');
          }
        });
      }
    }

    return Promise.reject(error);
  }
);

// Deduplicacion de peticiones GET identicas en vuelo para evitar tormentas de peticiones simultaneas
const originalGet = api.get.bind(api);
api.get = (url, config = {}) => {
  const paramsKey = config?.params ? JSON.stringify(config.params) : '';
  const cacheKey = `${url}?${paramsKey}`;

  if (inFlightGetRequests.has(cacheKey)) {
    return inFlightGetRequests.get(cacheKey);
  }

  const promise = originalGet(url, config).finally(() => {
    inFlightGetRequests.delete(cacheKey);
  });

  inFlightGetRequests.set(cacheKey, promise);
  return promise;
};

export default api;
