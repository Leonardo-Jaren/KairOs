import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useCampusTecnologico } from '@/composables/espacios/useCampusTecnologico';
import { useAuthStore } from '@/stores/auth';

const buildings = [
  { id: 1, codigo: 'EDIF-01', nombre: 'Edificio 1', activo: true },
  { id: 2, codigo: 'EDIF-02', nombre: 'Edificio 2', activo: true },
];
const spaces = [
  { id: 1, codigo_espacio: 'LAB-101', tipo: 'laboratorio', tipo_display: 'Laboratorio', edificio_id: 1, piso: '1', cantidad_equipos: 8, resumen_equipos: {}, activo: true },
  { id: 2, codigo_espacio: 'AULA-201', tipo: 'aula', tipo_display: 'Aula', edificio_id: 1, piso: '2', cantidad_equipos: 1, resumen_equipos: {}, activo: true },
  { id: 3, codigo_espacio: 'OF-101', tipo: 'oficina', tipo_display: 'Oficina', edificio_id: 2, piso: '1', cantidad_equipos: 2, resumen_equipos: {}, activo: true },
];

const createServices = () => ({
  spaceService: {
    listar: vi.fn().mockResolvedValue({ results: structuredClone(spaces) }),
    crear: vi.fn().mockResolvedValue(spaces[0]),
    actualizar: vi.fn().mockResolvedValue(spaces[0]),
    desactivar: vi.fn().mockResolvedValue(undefined),
  },
  buildingService: {
    listar: vi.fn().mockResolvedValue({ results: structuredClone(buildings) }),
    crear: vi.fn().mockResolvedValue({ id: 3, codigo: 'EDIF-03', nombre: 'Edificio 3', activo: true }),
    actualizar: vi.fn().mockResolvedValue(buildings[0]),
    desactivar: vi.fn().mockResolvedValue(undefined),
  },
});

const mountComposable = (services) => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  useAuthStore().user = { id: 10, rol: 'admin' };
  mount(defineComponent({
    setup() {
      state = useCampusTecnologico(services.spaceService, services.buildingService);
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });
  return state;
};

describe('useCampusTecnologico', () => {
  let services;

  beforeEach(() => {
    services = createServices();
  });

  it('agrupa laboratorios, aulas y oficinas por edificio y piso', async () => {
    const state = mountComposable(services);
    await flushPromises();

    expect(state.edificios.value).toHaveLength(2);
    expect(state.edificioActivo.value.spaces).toHaveLength(2);
    expect(state.pisosVisibles.value.map((floor) => floor.key)).toEqual(['1', '2']);
    expect(state.stats.value).toMatchObject({ laboratorios: 1, aulas: 1, ambientes: 3 });
  });

  it('crea edificios desde la vista de campus', async () => {
    const state = mountComposable(services);
    await flushPromises();
    state.openCreateBuilding();
    Object.assign(state.buildingForm, { codigo: 'EDIF-03', nombre: 'Edificio 3' });

    await state.submitBuilding();

    expect(services.buildingService.crear).toHaveBeenCalledWith(expect.objectContaining({
      codigo: 'EDIF-03',
      nombre: 'Edificio 3',
    }));
    expect(state.toast.type).toBe('success');
  });

  it('crea un ambiente en el piso seleccionado', async () => {
    const state = mountComposable(services);
    await flushPromises();
    state.openCreateSpace('2');
    Object.assign(state.spaceForm, { codigo_espacio: 'LAB-202', tipo: 'laboratorio' });

    await state.submitSpace();

    expect(services.spaceService.crear).toHaveBeenCalledWith(expect.objectContaining({
      codigo_espacio: 'LAB-202',
      edificio_id: 1,
      piso: '2',
    }));
  });

  it('mantiene visible el campus mientras refresca después de editar', async () => {
    const state = mountComposable(services);
    await flushPromises();

    let resolveBuildings;
    let resolveSpaces;
    services.buildingService.listar.mockReturnValueOnce(new Promise((resolve) => {
      resolveBuildings = resolve;
    }));
    services.spaceService.listar.mockReturnValueOnce(new Promise((resolve) => {
      resolveSpaces = resolve;
    }));

    state.openEditBuilding(state.edificios.value[0]);
    state.buildingForm.nombre = 'Edificio renovado';
    const submission = state.submitBuilding();
    await flushPromises();

    expect(state.loading.value).toBe(false);
    expect(state.edificios.value).toHaveLength(2);

    resolveBuildings({ results: structuredClone(buildings) });
    resolveSpaces({ results: structuredClone(spaces) });
    await submission;
  });
});
