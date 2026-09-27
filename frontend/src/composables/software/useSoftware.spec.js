import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useSoftware } from '@/composables/software/useSoftware';
import { useAuthStore } from '@/stores/auth';

const mockProductos = {
  count: 1,
  results: [
    {
      id: 1,
      software: 'VS Code',
      version: '1.93',
      tipo_licencia: 'libre',
      tipo_licencia_display: 'Libre / Open Source',
      licencias_totales: 100,
      licencias_usadas: 20,
      licencias_disponibles: 80,
    },
  ],
};

const createService = () => ({
  listar: vi.fn().mockResolvedValue(mockProductos),
  obtenerEstadisticas: vi.fn().mockResolvedValue({
    total_productos: 1,
    licencias_por_expirar: 0,
    productos_sobre_uso: 0,
  }),
  crear: vi.fn().mockResolvedValue(mockProductos.results[0]),
  actualizar: vi.fn().mockResolvedValue(mockProductos.results[0]),
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
        state = useSoftware(service);
        return () => h('div');
      },
    }),
  );
  return { state, wrapper };
};

describe('useSoftware', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('carga los productos y estadísticas al montar', async () => {
    const service = createService();
    const { state } = mountComposable(service);
    await flushPromises();

    expect(service.listar).toHaveBeenCalled();
    expect(service.obtenerEstadisticas).toHaveBeenCalled();
    expect(state.productos.value).toHaveLength(1);
    expect(state.stats.total_productos).toBe(1);
  });

  it('exportToExcel llama a service.exportarExcel con los filtros actuales', async () => {
    const service = createService();
    const { state } = mountComposable(service);
    await flushPromises();

    // Mock createObjectURL & DOM click
    global.URL.createObjectURL = vi.fn().mockReturnValue('blob:test');
    global.URL.revokeObjectURL = vi.fn();
    const linkMock = { href: '', setAttribute: vi.fn(), click: vi.fn() };
    vi.spyOn(document, 'createElement').mockReturnValue(linkMock);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => {});
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => {});

    state.filters.search = 'VS Code';
    state.filters.tipo_licencia = 'libre';

    await state.exportToExcel();

    expect(service.exportarExcel).toHaveBeenCalledWith({
      search: 'VS Code',
      tipo_licencia: 'libre',
    });
    expect(linkMock.click).toHaveBeenCalled();
  });
});
