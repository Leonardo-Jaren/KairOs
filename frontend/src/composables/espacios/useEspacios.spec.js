import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useEspacios } from '@/composables/espacios/useEspacios';
import { useAuthStore } from '@/stores/auth';

const space = {
  id: 1,
  codigo_espacio: 'LAB-301',
  tipo: 'laboratorio',
  tipo_display: 'Laboratorio',
  pabellon: 'Pabellón 3',
  edificio_id: 3,
  piso: '3',
  activo: true,
  responsable: null,
  cantidad_equipos: 0,
};

const createService = () => ({
  listar: vi.fn().mockResolvedValue({ count: 1, results: [space] }),
  obtenerEstadisticas: vi.fn().mockResolvedValue({
    total: 1,
    activos: 1,
    laboratorios: 1,
    equipos: 0,
  }),
  crear: vi.fn().mockResolvedValue(space),
  actualizar: vi.fn().mockResolvedValue(space),
  desactivar: vi.fn().mockResolvedValue(undefined),
});

const buildingService = {
  listar: vi.fn().mockResolvedValue({
    results: [{ id: 3, codigo: 'EDIF-03', nombre: 'Pabellón 3' }],
  }),
};

const mountComposable = (service, role = 'admin') => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  useAuthStore().user = { id: 99, nombre: 'Ada', rol: role };
  mount(defineComponent({
    setup() {
      state = useEspacios(service, buildingService);
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });
  return state;
};

describe('useEspacios', () => {
  let service;

  beforeEach(() => {
    service = createService();
  });

  it('carga listado e indicadores al montar', async () => {
    const state = mountComposable(service);
    await flushPromises();

    expect(service.listar).toHaveBeenCalledOnce();
    expect(service.obtenerEstadisticas).toHaveBeenCalledOnce();
    expect(state.espacios.value).toHaveLength(1);
    expect(state.stats.laboratorios).toBe(1);
  });

  it('mantiene al tecnico en modo de solo lectura', async () => {
    const state = mountComposable(service, 'tecnico');
    await flushPromises();

    expect(state.canEdit.value).toBe(false);
  });

  it('valida los campos obligatorios antes de crear', async () => {
    const state = mountComposable(service);
    await flushPromises();
    state.openCreate();

    const result = await state.submit();

    expect(result).toBe(false);
    expect(service.crear).not.toHaveBeenCalled();
    expect(state.formErrors.codigo_espacio).toBeTruthy();
    expect(state.formErrors.edificio_id).toBeTruthy();
  });

  it('crea un espacio y actualiza los datos', async () => {
    const state = mountComposable(service);
    await flushPromises();
    state.openCreate();
    Object.assign(state.form, {
      codigo_espacio: 'LAB-301',
      tipo: 'laboratorio',
      edificio_id: 3,
      piso: '3',
    });

    const result = await state.submit();

    expect(result).toBe(true);
    expect(service.crear).toHaveBeenCalledWith(expect.objectContaining({
      codigo_espacio: 'LAB-301',
      edificio_id: 3,
    }));
    expect(state.toast.type).toBe('success');
  });

  it('desactiva el espacio seleccionado', async () => {
    const state = mountComposable(service);
    await flushPromises();
    state.askDelete(space);

    await state.confirmDelete();

    expect(service.desactivar).toHaveBeenCalledWith(1);
    expect(state.deleteModalOpen.value).toBe(false);
  });
});
