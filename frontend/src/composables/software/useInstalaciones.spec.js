import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useInstalaciones } from '@/composables/software/useInstalaciones';
import { useAuthStore } from '@/stores/auth';

const mockInstalaciones = {
  count: 1,
  results: [
    {
      id: 10,
      equipo: 4,
      equipo_codigo: 'LAB101-PC01',
      producto_software: 1,
      producto_software_nombre: 'VS Code v1.93',
      numero_licencia_usado: 'LIC-001',
      fecha_instalacion: '2026-03-01',
    },
  ],
};

const createService = () => ({
  listar: vi.fn().mockResolvedValue(mockInstalaciones),
  crear: vi.fn().mockResolvedValue(mockInstalaciones.results[0]),
  actualizar: vi.fn().mockResolvedValue(mockInstalaciones.results[0]),
  eliminar: vi.fn().mockResolvedValue(undefined),
  exportarExcel: vi.fn().mockResolvedValue(new Blob(['fake-excel-data'])),
});

const mountComposable = (service = createService(), role = 'admin') => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  const authStore = useAuthStore();
  authStore.user = { id: 1, nombre: 'Admin', rol: role };

  const wrapper = mount(
    defineComponent({
      setup() {
        state = useInstalaciones(service);
        return () => h('div');
      },
    }),
  );
  return { state, wrapper };
};

describe('useInstalaciones', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('exportToExcel llama a service.exportarExcel con los filtros activos', async () => {
    const service = createService();
    const { state } = mountComposable(service);

    global.URL.createObjectURL = vi.fn().mockReturnValue('blob:test');
    global.URL.revokeObjectURL = vi.fn();
    const linkMock = { href: '', setAttribute: vi.fn(), click: vi.fn() };
    vi.spyOn(document, 'createElement').mockReturnValue(linkMock);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => {});
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => {});

    state.filters.search = 'PC01';
    state.filters.equipo_id = 4;

    await state.exportToExcel();

    expect(service.exportarExcel).toHaveBeenCalledWith({
      search: 'PC01',
      equipo_id: 4,
      espacio_id: undefined,
      producto_software_id: undefined,
    });
    expect(linkMock.click).toHaveBeenCalled();
  });
});
