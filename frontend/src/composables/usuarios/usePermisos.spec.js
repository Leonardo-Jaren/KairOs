import { describe, expect, it, vi } from 'vitest';

import { usePermisos } from '@/composables/usuarios/usePermisos';

const mockPermisosResponse = {
  usuario_id: 10,
  nombre_completo: 'Carlos Encargado',
  rol: 'responsable',
  permisos_base: {
    espacios: { ver: true, crear: true, editar: true, eliminar: true },
    equipos: { ver: true, crear: true, editar: true, eliminar: false },
    mantenimiento: { ver: true, crear: true, editar: true, eliminar: false },
    incidencias: { ver: true, crear: true, editar: true, eliminar: true },
    software: { ver: true, crear: true, editar: true, eliminar: false },
    usuarios: { ver: true, crear: true, editar: true, eliminar: false },
    auditoria: { ver: true, crear: false, editar: false, eliminar: false },
  },
  permisos_personalizados: [
    { modulo: 'equipos', accion: 'eliminar', permitido: true },
  ],
  permisos_efectivos: {
    espacios: { ver: true, crear: true, editar: true, eliminar: true },
    equipos: { ver: true, crear: true, editar: true, eliminar: true },
    mantenimiento: { ver: true, crear: true, editar: true, eliminar: false },
    incidencias: { ver: true, crear: true, editar: true, eliminar: true },
    software: { ver: true, crear: true, editar: true, eliminar: false },
    usuarios: { ver: true, crear: true, editar: true, eliminar: false },
    auditoria: { ver: true, crear: false, editar: false, eliminar: false },
  },
};

const createMockService = () => ({
  obtenerPermisos: vi.fn().mockResolvedValue(mockPermisosResponse),
  guardarPermisos: vi.fn().mockResolvedValue({
    ...mockPermisosResponse,
    permisos_efectivos: {
      ...mockPermisosResponse.permisos_efectivos,
      espacios: { ver: true, crear: false, editar: false, eliminar: false },
    },
  }),
  restablecerPermisos: vi.fn().mockResolvedValue({
    ...mockPermisosResponse,
    permisos_efectivos: mockPermisosResponse.permisos_base,
  }),
});

describe('usePermisos', () => {
  it('carga la configuración de permisos del usuario', async () => {
    const service = createMockService();
    const composable = usePermisos(service);

    await composable.cargarPermisos(10);

    expect(service.obtenerPermisos).toHaveBeenCalledWith(10);
    expect(composable.usuarioNombre.value).toBe('Carlos Encargado');
    expect(composable.usuarioRol.value).toBe('responsable');
    expect(composable.permisosEfectivos.equipos.eliminar).toBe(true);
    expect(composable.totalPersonalizados.value).toBe(1);
  });

  it('permite alternar un permiso granular', async () => {
    const service = createMockService();
    const composable = usePermisos(service);
    await composable.cargarPermisos(10);

    expect(composable.permisosEfectivos.equipos.eliminar).toBe(true);
    composable.togglePermiso('equipos', 'eliminar');
    expect(composable.permisosEfectivos.equipos.eliminar).toBe(false);
  });

  it('guarda los cambios en la matriz de permisos', async () => {
    const service = createMockService();
    const composable = usePermisos(service);
    await composable.cargarPermisos(10);

    const result = await composable.guardar();

    expect(result).toBe(true);
    expect(service.guardarPermisos).toHaveBeenCalledWith(
      10,
      expect.arrayContaining([
        expect.objectContaining({ modulo: 'equipos', accion: 'eliminar' }),
      ]),
    );
    expect(composable.successMessage.value).toBeTruthy();
  });

  it('restablece los permisos a los valores estándar del rol', async () => {
    const service = createMockService();
    const composable = usePermisos(service);
    await composable.cargarPermisos(10);

    const result = await composable.restablecer();

    expect(result).toBe(true);
    expect(service.restablecerPermisos).toHaveBeenCalledWith(10);
  });

  it('detecta correctamente permisos personalizados con isCustomized', async () => {
    const service = createMockService();
    const composable = usePermisos(service);
    await composable.cargarPermisos(10);

    // equipos.eliminar está personalizado a true (base es false)
    expect(composable.isCustomized('equipos', 'eliminar')).toBe(true);
    // espacios.ver no está modificado (base y efectivo son true)
    expect(composable.isCustomized('espacios', 'ver')).toBe(false);
  });
});

