import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, it } from 'vitest';

import { ROLE_BASE_PERMISSIONS, useAuthStore } from '@/stores/auth';

describe('authStore - hasPermission y ROLE_BASE_PERMISSIONS', () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useAuthStore();
  });

  it('retorna false si no hay usuario autenticado', () => {
    store.user = null;
    expect(store.hasPermission('espacios', 'ver')).toBe(false);
    expect(store.hasPermission('software', 'ver')).toBe(false);
  });

  it('superadmin tiene acceso irrestricto a todos los modulos y acciones', () => {
    store.user = { rol: 'superadmin' };
    expect(store.hasPermission('espacios', 'eliminar')).toBe(true);
    expect(store.hasPermission('auditoria', 'eliminar')).toBe(true);
  });

  it('docente solo tiene ver en software y ver/crear/editar en incidencias por defecto', () => {
    store.user = { rol: 'docente' };

    expect(store.hasPermission('espacios', 'ver')).toBe(false);
    expect(store.hasPermission('equipos', 'ver')).toBe(false);
    expect(store.hasPermission('mantenimiento', 'ver')).toBe(false);
    expect(store.hasPermission('usuarios', 'ver')).toBe(false);
    expect(store.hasPermission('auditoria', 'ver')).toBe(false);

    expect(store.hasPermission('software', 'ver')).toBe(true);
    expect(store.hasPermission('software', 'crear')).toBe(false);

    expect(store.hasPermission('incidencias', 'ver')).toBe(true);
    expect(store.hasPermission('incidencias', 'crear')).toBe(true);
    expect(store.hasPermission('incidencias', 'editar')).toBe(true);
    expect(store.hasPermission('incidencias', 'eliminar')).toBe(false);
  });

  it('usuario regular solo tiene ver en software y ver/crear en incidencias', () => {
    store.user = { rol: 'usuario' };

    expect(store.hasPermission('espacios', 'ver')).toBe(false);
    expect(store.hasPermission('equipos', 'ver')).toBe(false);
    expect(store.hasPermission('software', 'ver')).toBe(true);
    expect(store.hasPermission('incidencias', 'ver')).toBe(true);
    expect(store.hasPermission('incidencias', 'crear')).toBe(true);
    expect(store.hasPermission('incidencias', 'editar')).toBe(false);
  });

  it('tecnico mantiene permisos operativos sobre hardware y software', () => {
    store.user = { rol: 'tecnico' };

    expect(store.hasPermission('espacios', 'ver')).toBe(true);
    expect(store.hasPermission('espacios', 'crear')).toBe(false);
    expect(store.hasPermission('equipos', 'crear')).toBe(true);
    expect(store.hasPermission('mantenimiento', 'editar')).toBe(true);
    expect(store.hasPermission('software', 'ver')).toBe(true);
    expect(store.hasPermission('incidencias', 'crear')).toBe(true);
    expect(store.hasPermission('usuarios', 'ver')).toBe(true);
    expect(store.hasPermission('usuarios', 'crear')).toBe(false);
    expect(store.hasPermission('usuarios', 'editar')).toBe(false);
    expect(store.hasPermission('usuarios', 'eliminar')).toBe(false);
  });

  it('prioriza los permisos efectivos del backend si estan presentes', () => {
    store.user = {
      rol: 'docente',
      permisos_efectivos: {
        espacios: { ver: true, crear: false, editar: false, eliminar: false },
        software: { ver: false, crear: false, editar: false, eliminar: false },
      },
    };

    // Con override granular concedido en espacios
    expect(store.hasPermission('espacios', 'ver')).toBe(true);
    // Con override granular revocado en software
    expect(store.hasPermission('software', 'ver')).toBe(false);
  });

  it('asume la accion ver por defecto si el segundo argumento es omitido', () => {
    store.user = { rol: 'docente' };
    expect(store.hasPermission('software')).toBe(true);
    expect(store.hasPermission('espacios')).toBe(false);
  });

  it('responsable mantiene gestion sobre espacios, equipos, mantenimiento, incidencias, software y usuarios', () => {
    store.user = { rol: 'responsable' };
    expect(store.hasPermission('espacios', 'ver')).toBe(true);
    expect(store.hasPermission('espacios', 'crear')).toBe(true);
    expect(store.hasPermission('equipos', 'ver')).toBe(true);
    expect(store.hasPermission('equipos', 'crear')).toBe(true);
    expect(store.hasPermission('mantenimiento', 'ver')).toBe(true);
    expect(store.hasPermission('incidencias', 'ver')).toBe(true);
    expect(store.hasPermission('software', 'ver')).toBe(true);
    expect(store.hasPermission('usuarios', 'ver')).toBe(true);
    expect(store.hasPermission('auditoria', 'ver')).toBe(true);
  });

  it('coincide exactamente la estructura de ROLE_BASE_PERMISSIONS con los 6 roles', () => {
    expect(ROLE_BASE_PERMISSIONS).toHaveProperty('superadmin');
    expect(ROLE_BASE_PERMISSIONS).toHaveProperty('admin');
    expect(ROLE_BASE_PERMISSIONS).toHaveProperty('responsable');
    expect(ROLE_BASE_PERMISSIONS).toHaveProperty('tecnico');
    expect(ROLE_BASE_PERMISSIONS).toHaveProperty('docente');
    expect(ROLE_BASE_PERMISSIONS).toHaveProperty('usuario');

    expect(ROLE_BASE_PERMISSIONS.docente.espacios.ver).toBe(false);
    expect(ROLE_BASE_PERMISSIONS.docente.equipos.ver).toBe(false);
    expect(ROLE_BASE_PERMISSIONS.docente.software.ver).toBe(true);
    expect(ROLE_BASE_PERMISSIONS.docente.incidencias.editar).toBe(true);
  });

  it('fetchProfile actualiza el usuario y permisos en Pinia y localStorage', async () => {
    const authService = (await import('@/services/auth.service')).default;
    const vi = (await import('vitest')).vi;
    const mockMeData = {
      id: 40,
      correo: 'jorge@kairos.test',
      nombre: 'Jorge',
      apellido: 'Alvarez',
      rol: 'tecnico',
      permisos_efectivos: {
        software: { ver: false, crear: false, editar: false, eliminar: false },
      },
    };
    const spy = vi.spyOn(authService, 'getMe').mockResolvedValue(mockMeData);

    store.accessToken = 'dummy-token';
    store.user = { id: 40, rol: 'tecnico', permisos_efectivos: { software: { ver: true } } };

    const result = await store.fetchProfile();
    expect(spy).toHaveBeenCalled();
    expect(result.permisos_efectivos.software.ver).toBe(false);
    expect(store.user.permisos_efectivos.software.ver).toBe(false);

    const storedUser = JSON.parse(localStorage.getItem('kairos_user'));
    expect(storedUser.permisos_efectivos.software.ver).toBe(false);

    spy.mockRestore();
  });

  it('fetchProfile no realiza peticion HTTP si no ha transcurrido el tiempo minimo (throttling)', async () => {
    const authService = (await import('@/services/auth.service')).default;
    const vi = (await import('vitest')).vi;
    const spy = vi.spyOn(authService, 'getMe').mockResolvedValue({ id: 40, rol: 'tecnico' });

    store.accessToken = 'dummy-token';
    store.user = { id: 40, rol: 'tecnico' };

    // Primera llamada ejecuta la consulta al backend
    await store.fetchProfile();
    expect(spy).toHaveBeenCalledTimes(1);

    // Segunda llamada inmediata dentro de los 30s no debe llamar a getMe
    await store.fetchProfile();
    expect(spy).toHaveBeenCalledTimes(1);

    // Con force: true sí debe consultar inmediatamente al backend
    await store.fetchProfile({ force: true });
    expect(spy).toHaveBeenCalledTimes(2);

    spy.mockRestore();
  });

  it('fetchProfile deduplica consultas concurrentes en una unica promesa', async () => {
    const authService = (await import('@/services/auth.service')).default;
    const vi = (await import('vitest')).vi;
    let resolvePromise;
    const deferred = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    const spy = vi.spyOn(authService, 'getMe').mockImplementation(() => deferred);

    store.accessToken = 'dummy-token';
    store.user = { id: 40, rol: 'tecnico' };

    // Disparar dos llamadas simultaneas (como sucede al activar ventana con focus y visibilitychange)
    const p1 = store.fetchProfile({ force: true });
    const p2 = store.fetchProfile({ force: true });

    // Se deduplica internamente disparando solo 1 peticion a authService.getMe
    expect(spy).toHaveBeenCalledTimes(1);

    resolvePromise({ id: 40, rol: 'tecnico' });
    const [res1, res2] = await Promise.all([p1, p2]);

    expect(spy).toHaveBeenCalledTimes(1);
    expect(res1).toEqual(res2);
    expect(res1.id).toBe(40);

    spy.mockRestore();
  });

  it('fetchProfile actualiza lastProfileFetchTimestamp tras un fallo para evitar rafagas de reintentos', async () => {
    const authService = (await import('@/services/auth.service')).default;
    const vi = (await import('vitest')).vi;
    const spy = vi.spyOn(authService, 'getMe').mockRejectedValue(new Error('Network error'));

    store.accessToken = 'dummy-token';
    store.user = { id: 40, rol: 'tecnico' };
    store.lastProfileFetchTimestamp = 0;

    const result = await store.fetchProfile({ force: true });
    expect(result).toBeNull();
    expect(store.lastProfileFetchTimestamp).toBeGreaterThan(0);

    // Segunda llamada no forzada no debe invocar getMe debido al cooldown
    await store.fetchProfile();
    expect(spy).toHaveBeenCalledTimes(1);

    spy.mockRestore();
  });

  it('fetchProfile ejecuta logout si el servidor responde con 401 Unauthorized', async () => {
    const authService = (await import('@/services/auth.service')).default;
    const vi = (await import('vitest')).vi;
    const error401 = new Error('Unauthorized');
    error401.response = { status: 401 };
    const spy = vi.spyOn(authService, 'getMe').mockRejectedValue(error401);
    const logoutSpy = vi.spyOn(store, 'logout');

    store.accessToken = 'dummy-token';
    store.user = { id: 40, rol: 'tecnico' };

    const result = await store.fetchProfile({ force: true });
    expect(result).toBeNull();
    expect(logoutSpy).toHaveBeenCalled();

    spy.mockRestore();
  });
});
