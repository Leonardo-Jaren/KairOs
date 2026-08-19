import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  formatCountLabel,
  useCampusTecnologico,
} from '@/composables/espacios/useCampusTecnologico';
import { normalizeFloorLayout } from '@/composables/espacios/useCroquisPiso';
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
    guardarCroquisPiso: vi.fn().mockImplementation(async (_id, payload) => ({
      ...buildings[0],
      configuracion_croquis: { version: 1, pisos: { [payload.piso]: payload } },
    })),
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

  it('formatea métricas en singular y plural', () => {
    expect(formatCountLabel(1, 'piso', 'pisos')).toBe('piso');
    expect(formatCountLabel(2, 'piso', 'pisos')).toBe('pisos');
    expect(formatCountLabel(1, 'ambiente', 'ambientes')).toBe('ambiente');
    expect(formatCountLabel(1, 'equipo', 'equipos')).toBe('equipo');
  });

  it('agrupa laboratorios, aulas y oficinas por edificio y piso', async () => {
    const state = mountComposable(services);
    await flushPromises();

    expect(state.edificios.value).toHaveLength(2);
    expect(state.edificioActivo.value.spaces).toHaveLength(2);
    expect(state.pisosVisibles.value.map((floor) => floor.key)).toEqual(['1', '2']);
    expect(state.activeFloor.value.key).toBe('2');
    expect(state.stats.value).toMatchObject({ laboratorios: 1, aulas: 1, ambientes: 3 });
  });

  it('navega un piso a la vez empezando por el piso 2', async () => {
    const state = mountComposable(services);
    await flushPromises();

    expect(state.activeFloor.value.key).toBe('2');
    state.showPreviousFloor();
    expect(state.activeFloor.value.key).toBe('1');
    state.showNextFloor();
    expect(state.activeFloor.value.key).toBe('2');
  });

  it('balancea la cuadrícula según la cantidad de edificios', async () => {
    services.buildingService.listar.mockResolvedValue({
      results: Array.from({ length: 6 }, (_, index) => ({
        id: index + 1,
        codigo: `EDIF-0${index + 1}`,
        nombre: `Edificio ${index + 1}`,
        activo: true,
      })),
    });
    const state = mountComposable(services);
    await flushPromises();

    expect(state.buildingColumnCount.value).toBe(6);
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
    state.openCreateSpace('Piso 2');
    Object.assign(state.spaceForm, { codigo_espacio: 'LAB-202', tipo: 'laboratorio' });

    expect(state.spaceForm.piso).toBe('2');

    await state.submitSpace();

    expect(services.spaceService.crear).toHaveBeenCalledWith(expect.objectContaining({
      codigo_espacio: 'LAB-202',
      edificio_id: 1,
      piso: '2',
    }));
  });

  it('rechaza un piso que no contiene únicamente números', async () => {
    const state = mountComposable(services);
    await flushPromises();
    state.openCreateSpace();
    Object.assign(state.spaceForm, {
      codigo_espacio: 'LAB-202',
      tipo: 'laboratorio',
      edificio_id: 1,
      piso: 'Piso 2',
    });

    await state.submitSpace();

    expect(state.spaceErrors.piso).toBe('El piso debe contener únicamente números.');
    expect(services.spaceService.crear).not.toHaveBeenCalled();
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

  it('genera un croquis inicial que diferencia ambientes y reserva pasillos', async () => {
    const state = mountComposable(services);
    await flushPromises();

    const firstFloor = state.pisosVisibles.value.find((floor) => floor.key === '1');
    const secondFloor = state.pisosVisibles.value.find((floor) => floor.key === '2');
    const laboratory = firstFloor.layout.ambientes.find((room) => room.espacio_id === 1);
    const classroom = secondFloor.layout.ambientes.find((room) => room.espacio_id === 2);

    expect(laboratory).toMatchObject({ ancho: 3, alto: 2 });
    expect(classroom).toMatchObject({ ancho: 1, alto: 1 });
    expect(firstFloor.layout.pasillos).toHaveLength(firstFloor.layout.columnas);
  });

  it('agrega ambientes nuevos sin reiniciar las posiciones guardadas del piso', () => {
    const storedLayout = {
      filas: 5,
      columnas: 12,
      ambientes: [
        { espacio_id: 1, fila: 3, columna: 7, ancho: 3, alto: 2 },
        { espacio_id: 2, fila: 1, columna: 5, ancho: 1, alto: 1 },
      ],
      pasillos: [{ fila: 2, columna: 1 }, { fila: 2, columna: 2 }],
    };
    const floorSpaces = [
      spaces[0],
      spaces[1],
      { id: 4, codigo_espacio: 'LAB-202', tipo: 'laboratorio', cantidad_equipos: 4 },
    ];

    const layout = normalizeFloorLayout(storedLayout, floorSpaces);

    expect(layout.ambientes.find((room) => room.espacio_id === 1)).toEqual(
      storedLayout.ambientes[0],
    );
    expect(layout.ambientes.find((room) => room.espacio_id === 2)).toEqual(
      storedLayout.ambientes[1],
    );
    expect(layout.pasillos).toEqual(storedLayout.pasillos);
    expect(layout.ambientes.find((room) => room.espacio_id === 4)).toBeDefined();
  });

  it('guarda el croquis del piso sin recargar toda la vista', async () => {
    const state = mountComposable(services);
    await flushPromises();
    const floor = state.pisosVisibles.value.find((item) => item.key === '1');

    state.startFloorEditing(floor);
    state.updateFloorColumns(14);
    await state.saveFloorLayout();

    expect(services.buildingService.guardarCroquisPiso).toHaveBeenCalledWith(1, expect.objectContaining({
      piso: '1',
      columnas: 14,
      ambientes: expect.arrayContaining([expect.objectContaining({ espacio_id: 1 })]),
    }));
    expect(state.editingFloor.value).toBe('');
    expect(state.loading.value).toBe(false);
  });
});
