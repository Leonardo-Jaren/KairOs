import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

describe('api.js interceptors', () => {
  let authStore;

  beforeEach(() => {
    setActivePinia(createPinia());
    authStore = useAuthStore();
    vi.clearAllMocks();
  });

  it('adjunta la cabecera Authorization con el token de acceso en peticiones salientes', async () => {
    authStore.accessToken = 'jwt-token-123';

    // Obtener la funcion interceptora de peticion
    const requestInterceptor = api.interceptors.request.handlers[0].fulfilled;
    const config = { headers: {} };

    const result = await requestInterceptor(config);
    expect(result.headers.Authorization).toBe('Bearer jwt-token-123');
  });

  it('no adjunta Authorization si no existe accessToken', async () => {
    authStore.accessToken = null;

    const requestInterceptor = api.interceptors.request.handlers[0].fulfilled;
    const config = { headers: {} };

    const result = await requestInterceptor(config);
    expect(result.headers.Authorization).toBeUndefined();
  });

  it('deduplica peticiones GET concurrentes identicas compartiendo la misma promesa', async () => {
    let resolveFirst;
    const mockPromise = new Promise((resolve) => {
      resolveFirst = resolve;
    });

    const originalAdapter = api.defaults.adapter;
    api.defaults.adapter = () => mockPromise;

    try {
      const call1 = api.get('/api/v1/espacios/locales/', { params: { activo: true } });
      const call2 = api.get('/api/v1/espacios/locales/', { params: { activo: true } });

      // Deben retornar exactamente la misma instancia de promesa
      expect(call1).toBe(call2);

      resolveFirst({
        data: [{ id: 1, nombre: 'Local Central' }],
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {},
      });

      const [res1, res2] = await Promise.all([call1, call2]);
      expect(res1.data).toEqual([{ id: 1, nombre: 'Local Central' }]);
      expect(res2.data).toEqual([{ id: 1, nombre: 'Local Central' }]);
    } finally {
      api.defaults.adapter = originalAdapter;
    }
  });

  it('invoca fetchProfile cuando un endpoint regular responde 403 Forbidden', async () => {
    const fetchProfileSpy = vi.spyOn(authStore, 'fetchProfile').mockResolvedValue({});
    const responseErrorHandler = api.interceptors.response.handlers[0].rejected;

    const error = {
      config: { url: '/api/v1/usuarios/' },
      response: { status: 403 },
    };

    await expect(responseErrorHandler(error)).rejects.toEqual(error);
    expect(fetchProfileSpy).toHaveBeenCalledWith({ minIntervalMs: 5000 });
  });

  it('cierra sesion y no invoca fetchProfile si el propio endpoint /auth/me responde 403', async () => {
    const fetchProfileSpy = vi.spyOn(authStore, 'fetchProfile');
    const logoutSpy = vi.spyOn(authStore, 'logout');
    const routerPushSpy = vi.spyOn(router, 'push').mockImplementation(() => {});
    const responseErrorHandler = api.interceptors.response.handlers[0].rejected;

    const error = {
      config: { url: '/api/v1/auth/me/' },
      response: { status: 403 },
    };

    await expect(responseErrorHandler(error)).rejects.toEqual(error);

    // No debe llamar a fetchProfile para evitar recursion infinita
    expect(fetchProfileSpy).not.toHaveBeenCalled();
    // Debe cerrar sesion y redirigir
    expect(logoutSpy).toHaveBeenCalled();
    expect(routerPushSpy).toHaveBeenCalledWith('/login');
  });
});
