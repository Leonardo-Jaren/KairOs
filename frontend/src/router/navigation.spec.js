import { describe, expect, it } from 'vitest';

import router from '@/router';

describe('navegacion de modulos', () => {
  it('mantiene disponibles las rutas de usuarios y usuarios por espacio', () => {
    expect(router.resolve('/usuarios').name).toBe('Usuarios');
    expect(router.resolve('/espacios/usuarios').name).toBe('EspaciosUsuarios');
  });

  it('resuelve el listado y el detalle propios de espacios', () => {
    const resolved = router.resolve('/espacios');

    expect(resolved.name).toBe('Espacios');
    expect(router.resolve('/espacios/12').name).toBe('EspacioDetalle');
  });
});
