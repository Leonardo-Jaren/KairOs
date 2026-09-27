import { flushPromises, mount } from '@vue/test-utils';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useHistorial } from '@/composables/historial/useHistorial';

const mockEventos = {
  count: 2,
  results: [
    {
      id: 1,
      fecha: '2026-03-20T10:00:00Z',
      tipo_evento: 'equipo.creacion',
      modulo: 'equipo',
      object_id: 12,
      descripcion: 'Equipo creado en laboratorio',
      usuario_nombre: 'Admin General',
    },
    {
      id: 2,
      fecha: '2026-03-21T11:00:00Z',
      tipo_evento: 'espacio.modificacion',
      modulo: 'espacio',
      object_id: 5,
      descripcion: 'Capacidad modificada',
      usuario_nombre: 'Admin General',
    },
  ],
};

const createService = () => ({
  listar: vi.fn().mockResolvedValue(mockEventos),
  obtener: vi.fn().mockResolvedValue(mockEventos.results[0]),
  exportarExcel: vi.fn().mockResolvedValue(new Blob(['fake-excel-data'])),
});

const mountComposable = (service = createService()) => {
  let state;
  const wrapper = mount(
    defineComponent({
      setup() {
        state = useHistorial(service);
        return () => h('div');
      },
    }),
  );
  return { state, wrapper };
};

describe('useHistorial', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('carga eventos de auditoría al montar', async () => {
    const service = createService();
    const { state } = mountComposable(service);
    await flushPromises();

    expect(service.listar).toHaveBeenCalled();
    expect(state.historial.value).toHaveLength(2);
    expect(state.pagination.total).toBe(2);
  });

  it('exportToExcel invoca service.exportarExcel con los filtros activos', async () => {
    const service = createService();
    const { state } = mountComposable(service);
    await flushPromises();

    global.URL.createObjectURL = vi.fn().mockReturnValue('blob:test');
    global.URL.revokeObjectURL = vi.fn();
    const linkMock = { href: '', setAttribute: vi.fn(), click: vi.fn() };
    vi.spyOn(document, 'createElement').mockReturnValue(linkMock);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => {});
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => {});

    state.filters.modulo = 'equipo';
    state.filters.tipo_evento = 'equipo.creacion';

    await state.exportToExcel();

    expect(service.exportarExcel).toHaveBeenCalledWith({
      modulo: 'equipo',
      tipo_evento: 'equipo.creacion',
      usuario_id: undefined,
      fecha_desde: undefined,
      fecha_hasta: undefined,
    });
    expect(linkMock.click).toHaveBeenCalled();
  });
});
