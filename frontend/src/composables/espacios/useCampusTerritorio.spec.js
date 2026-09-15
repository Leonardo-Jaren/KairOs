import { flushPromises, mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { createMemoryHistory, createRouter, useRoute, useRouter } from 'vue-router';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { useAuthStore } from '@/stores/auth';
import { useCampusTecnologico } from '@/composables/espacios/useCampusTecnologico';
import { listarTodas } from '@/composables/espacios/useCampusTerritorio';

const locales = [
  { id: 1, codigo: 'HC', nombre: 'Local central', ciudad: 'Huánuco', activo: true },
  { id: 2, codigo: 'HE', nombre: 'La Esperanza', ciudad: 'Huánuco', activo: true },
  { id: 3, codigo: 'TM', nombre: 'Tingo María', ciudad: 'Tingo María', activo: true },
  { id: 4, codigo: 'HV', nombre: 'Local vacío', ciudad: 'Huánuco', activo: true },
];
const buildings = [1, 2, 2, 2, 2, 2, 2, 2, 3, 3, null].map((localId, index) => ({
  id: index + 1, codigo: `PAB-${index + 1}`, nombre: `Pabellón ${index + 1}`,
  local_id: localId, activo: true, configuracion_croquis: {},
}));
const spaces = buildings.map((building) => ({
  id: building.id, codigo_espacio: `LAB-${building.id}`, edificio_id: building.id,
  tipo: 'laboratorio', tipo_display: 'Laboratorio', piso: '2',
  cantidad_equipos: building.id, resumen_equipos: {}, activo: true,
}));
const wrappers = [];
afterEach(() => wrappers.splice(0).forEach((wrapper) => wrapper.unmount()));

async function createCampus({ path = '/espacios/mapa?local=1', role = 'admin', reject = false } = {}) {
  const data = { buildings: structuredClone(buildings), spaces: structuredClone(spaces), locales: structuredClone(locales) };
  const buildingService = {
    listar: vi.fn(async () => ({ results: data.buildings })),
    actualizar: vi.fn(async (id, payload) => {
      const building = data.buildings.find((item) => item.id === id);
      Object.assign(building, payload);
      return building;
    }),
    crear: vi.fn(),
    guardarCroquisPiso: vi.fn(),
  };
  const spaceService = { listar: vi.fn(async () => ({ results: data.spaces })), crear: vi.fn() };
  const localService = { listar: vi.fn(async () => {
    if (reject) throw new Error('Falló la conexión');
    return { results: data.locales };
  }), crear: vi.fn() };
  const router = createRouter({ history: createMemoryHistory(), routes: [
    { path: '/espacios/mapa', component: { render: () => null } },
    { path: '/espacios/:id', component: { render: () => null } },
  ] });
  await router.push(path);
  await router.isReady();
  let state;
  const wrapper = mount(defineComponent({ setup() {
    useAuthStore().user = { id: 1, rol: role };
    state = useCampusTecnologico(spaceService, buildingService, localService, { route: useRoute(), router: useRouter() });
    return () => h('div');
  } }), { global: { plugins: [createPinia(), router] } });
  wrappers.push(wrapper);
  await flushPromises();
  return { state, router, buildingService, localService, spaceService, data };
}

describe('mapa por locales', () => {
  it('aísla pabellones, indicadores y opciones de ambientes en los escenarios 1/7/2', async () => {
    const { state } = await createCampus();
    expect(state.edificios.value).toHaveLength(1);
    expect(state.edificioActivo.value.id).toBe(1);
    expect(state.stats.value).toMatchObject({ ambientes: 1, equipos: 1 });
    state.selectLocal(2);
    await flushPromises();
    expect(state.edificios.value).toHaveLength(7);
    expect(state.stats.value).toMatchObject({ ambientes: 7, equipos: 35 });
    expect(state.buildingOptions.value.map((item) => item.value)).toEqual([2, 3, 4, 5, 6, 7, 8]);
    state.selectCity('Tingo María');
    await flushPromises();
    expect(state.edificios.value).toHaveLength(2);
    expect(state.stats.value).toMatchObject({ ambientes: 2, equipos: 19 });
    expect(state.edificioActivo.value.spaces[0].edificio_id).toBe(9);
  });

  it('muestra un local vacío sin heredar ambientes y conserva acceso a registros anteriores', async () => {
    const { state } = await createCampus();
    state.selectLocal(4);
    await flushPromises();
    expect(state.edificioActivo.value).toBeNull();
    expect(state.activeFloor.value).toBeNull();
    expect(state.stats.value.ambientes).toBe(0);
    state.selectLocal('__legacy__');
    await flushPromises();
    expect(state.selectedLocalName.value).toBe('Sin local asignado');
    expect(state.edificioActivo.value.id).toBe(11);
    expect(state.allLocalOptions.value).toHaveLength(5);
  });

  it('respeta enlaces y vuelve al contexto previo con el historial del navegador', async () => {
    const { state, router } = await createCampus({ path: '/espacios/mapa?local=2&pabellon=7&otra=conservar' });
    expect(state.selectedBuildingId.value).toBe(7);
    state.selectLocal(3);
    await flushPromises();
    expect(router.currentRoute.value.query.local).toBe('3');
    expect(router.currentRoute.value.query.otra).toBe('conservar');
    router.back();
    await flushPromises();
    expect(state.selectedLocalId.value).toBe(2);
    expect(state.selectedBuildingId.value).toBe(7);
  });

  it('corrige una pareja local/pabellón incoherente sin mostrar otro local', async () => {
    const { state, router } = await createCampus({ path: '/espacios/mapa?local=1&pabellon=9' });
    expect(state.edificioActivo.value.id).toBe(1);
    expect(router.currentRoute.value.query.pabellon).toBe('1');
  });

  it('conserva el borrador frente a cambios de local, pabellón y ruta mientras se edita', async () => {
    const { state, router } = await createCampus();
    state.startFloorEditing(state.activeFloor.value);
    expect(state.selectLocal(2)).toBe(false);
    expect(state.selectBuilding(2)).toBe(false);
    state.openEditBuilding(state.edificioActivo.value);
    expect(state.buildingModalOpen.value).toBe(false);
    await router.push('/espacios/1');
    expect(router.currentRoute.value.path).toBe('/espacios/mapa');
    expect(state.editingFloor.value).toBe('2');
    state.cancelFloorEditing();
    state.selectLocal(2);
    await flushPromises();
    expect(state.selectedLocalId.value).toBe(2);
  });

  it('permite asignar un pabellón anterior a un local de otra ciudad y sigue su ubicación', async () => {
    const { state, buildingService } = await createCampus({ path: '/espacios/mapa?local=__legacy__' });
    state.openEditBuilding(state.edificioActivo.value);
    state.buildingForm.local_id = 3;
    await state.submitBuilding();
    await flushPromises();
    expect(buildingService.actualizar).toHaveBeenCalledWith(11, expect.objectContaining({ local_id: 3 }));
    expect(state.selectedCity.value).toBe('Tingo María');
    expect(state.selectedLocalId.value).toBe(3);
    expect(state.edificioActivo.value.id).toBe(11);
  });

  it('impide acciones administrativas en el composable para un técnico', async () => {
    const { state, localService, buildingService, spaceService } = await createCampus({ role: 'tecnico' });
    state.openCreateLocal();
    state.openCreateBuilding();
    state.openCreateSpace();
    await state.submitLocal();
    await state.submitBuilding();
    await state.submitSpace();
    expect(state.localModalOpen.value).toBe(false);
    expect(state.buildingModalOpen.value).toBe(false);
    expect(localService.crear).not.toHaveBeenCalled();
    expect(buildingService.crear).not.toHaveBeenCalled();
    expect(spaceService.crear).not.toHaveBeenCalled();
  });

  it('distingue errores de carga de un mapa vacío y permite reintentar', async () => {
    const { state, localService } = await createCampus({ reject: true });
    expect(state.error.value).toBeTruthy();
    localService.listar.mockResolvedValue({ results: locales });
    await state.loadCampus();
    await flushPromises();
    expect(state.error.value).toBe('');
    expect(state.edificios.value.length).toBeGreaterThan(0);
  });
});

describe('carga paginada del mapa', () => {
  it('conserva filtros y recupera páginas posteriores al límite de 100', async () => {
    const service = { listar: vi.fn()
      .mockResolvedValueOnce({ results: Array.from({ length: 100 }, (_, id) => ({ id })), count: 101, next: '?page=2' })
      .mockResolvedValueOnce({ results: [{ id: 100 }], count: 101, next: null }) };
    expect(await listarTodas(service, { activo: true })).toHaveLength(101);
    expect(service.listar).toHaveBeenLastCalledWith({ activo: true, page_size: 100, page: 2 });
  });
  it('rechaza ciclos e información incompleta en vez de calcular totales parciales', async () => {
    const service = { listar: vi.fn().mockResolvedValue({ results: [{ id: 1 }], next: '?page=1' }) };
    await expect(listarTodas(service)).rejects.toThrow('repitió');
    service.listar.mockResolvedValue({ results: [{ id: 1 }], next: null, count: 5 });
    await expect(listarTodas(service)).rejects.toThrow('completo');
  });
});
