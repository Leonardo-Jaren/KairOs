import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { usePlanoEspacio } from '@/composables/espacios/usePlanoEspacio';
import { useAuthStore } from '@/stores/auth';

const equipment = (id, estado = 'en_uso') => ({
  id,
  codigo: `PC-${id}`,
  tipo_equipo: 'desktop',
  tipo_equipo_display: 'Desktop',
  marca: 'Lenovo',
  modelo: 'ThinkCentre',
  estado,
  estado_display: estado === 'en_uso' ? 'En uso' : 'En mantenimiento',
});

const space = {
  id: 1,
  codigo_espacio: 'LAB-301',
  pabellon: 'Edificio 3',
  piso: '2',
  configuracion_plano: {},
  equipos: [equipment(1), equipment(2), equipment(3)],
};

const createServices = () => {
  const spaceService = {
    obtener: vi.fn().mockResolvedValue(structuredClone(space)),
    guardarDisposicion: vi.fn().mockImplementation(async (_id, payload) => ({
      ...structuredClone(space),
      configuracion_plano: payload,
    })),
  };
  const maintenanceService = {
    obtenerTecnicosDisponibles: vi.fn().mockResolvedValue([]),
    crear: vi.fn().mockResolvedValue({ id: 10 }),
  };
  return { spaceService, maintenanceService };
};

const mountComposable = (services, role = 'admin') => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  useAuthStore().user = { id: 99, nombre: 'Ada', rol: role };
  mount(defineComponent({
    setup() {
      state = usePlanoEspacio(1, services.spaceService, services.maintenanceService);
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });
  return state;
};

describe('usePlanoEspacio', () => {
  let services;

  beforeEach(() => {
    services = createServices();
  });

  it('distribuye automáticamente todos los equipos sin superponerlos', async () => {
    const state = mountComposable(services);
    await flushPromises();

    const occupied = state.cells.value.filter((cell) => cell.equipment);
    const keys = occupied.map((cell) => `${cell.row}-${cell.column}`);
    expect(occupied).toHaveLength(3);
    expect(new Set(keys).size).toBe(3);
  });

  it('guarda una posición movida y limita la edición al administrador', async () => {
    const state = mountComposable(services);
    await flushPromises();
    state.startEditing();
    const occupied = state.cells.value.find((cell) => cell.equipment?.id === 1);
    const empty = state.cells.value.find((cell) => !cell.equipment);

    state.handleCellClick(occupied);
    state.handleCellClick(empty);
    await state.saveLayout();

    expect(services.spaceService.guardarDisposicion).toHaveBeenCalledWith(1, expect.objectContaining({
      puestos: expect.arrayContaining([
        expect.objectContaining({ equipo_id: 1, fila: empty.row, columna: empty.column }),
      ]),
    }));

    const technicianState = mountComposable(createServices(), 'tecnico');
    await flushPromises();
    expect(technicianState.canEdit.value).toBe(false);
  });

  it('registra una falla y refleja el envío inmediato a mantenimiento', async () => {
    const state = mountComposable(services);
    await flushPromises();
    state.selectedEquipo.value = state.equipos.value[0];
    state.openReport();
    state.reportForm.descripcion = 'No muestra imagen.';

    await state.submitReport();

    expect(services.maintenanceService.crear).toHaveBeenCalledWith(expect.objectContaining({
      equipo_id: 1,
      tipo_mantenimiento: 'correctivo',
      estado: 'en_proceso',
    }));
    expect(state.equipos.value[0].estado).toBe('en_mantenimiento');
  });
});
