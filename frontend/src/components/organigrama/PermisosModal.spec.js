import { mount } from '@vue/test-utils';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import PermisosModal from '@/components/organigrama/PermisosModal.vue';
import permisosService from '@/services/permisos.service';

vi.mock('@/services/permisos.service', () => ({
  default: {
    obtenerPermisos: vi.fn().mockResolvedValue({
      usuario_id: 40,
      nombre_completo: 'Jorge Alvarez',
      rol: 'tecnico',
      permisos_base: {
        espacios: { ver: true, crear: false, editar: false, eliminar: false },
        equipos: { ver: true, crear: true, editar: true, eliminar: false },
        mantenimiento: { ver: true, crear: true, editar: true, eliminar: false },
        incidencias: { ver: true, crear: true, editar: true, eliminar: false },
        software: { ver: true, crear: true, editar: true, eliminar: false },
        usuarios: { ver: true, crear: false, editar: false, eliminar: false },
        auditoria: { ver: true, crear: false, editar: false, eliminar: false },
      },
      permisos_personalizados: [],
      permisos_efectivos: {
        espacios: { ver: true, crear: false, editar: false, eliminar: false },
        equipos: { ver: true, crear: true, editar: true, eliminar: false },
        mantenimiento: { ver: true, crear: true, editar: true, eliminar: false },
        incidencias: { ver: true, crear: true, editar: true, eliminar: false },
        software: { ver: true, crear: true, editar: true, eliminar: false },
        usuarios: { ver: true, crear: false, editar: false, eliminar: false },
        auditoria: { ver: true, crear: false, editar: false, eliminar: false },
      },
    }),
    guardarPermisos: vi.fn().mockResolvedValue({}),
    restablecerPermisos: vi.fn().mockResolvedValue({}),
  },
}));

describe('PermisosModal.vue', () => {
  const user = { id: 40, nombre_completo: 'Jorge Alvarez', rol: 'tecnico' };

  it('renderiza la matriz de permisos con los 7 módulos y sus iconos', async () => {
    const wrapper = mount(PermisosModal, {
      props: {
        open: true,
        user,
      },
      attachTo: document.body,
    });

    await vi.waitFor(() => {
      expect(document.body.textContent).toContain('Espacios y Ambientes');
    });

    expect(document.body.textContent).toContain('Equipos y Hardware');
    expect(document.body.textContent).toContain('Mantenimiento Preventivo / Correctivo');
    expect(document.body.textContent).toContain('Reporte y Gestión de Incidencias');
    expect(document.body.textContent).toContain('Software y Licencias');
    expect(document.body.textContent).toContain('Administración de Usuarios');
    expect(document.body.textContent).toContain('Auditoría y Trazabilidad');

    const rows = document.querySelectorAll('tbody tr');
    expect(rows).toHaveLength(7);

    wrapper.unmount();
  });
});
