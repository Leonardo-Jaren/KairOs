import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useDashboard } from '@/composables/dashboard/useDashboard';
import { useAuthStore } from '@/stores/auth';

const dashboardResponse = {
  data: {
    equipos: { total: 10, en_uso: 7, en_mantenimiento: 1, de_baja: 1 },
    espacios: { total: 4, activos: 3, laboratorios: 2, equipos: 10 },
    usuarios: { total: 10, activos: 8, administradores: 1, tecnicos: 3, docentes: 4 },
    mantenimiento: {
      total: 10,
      pendientes: 2,
      en_proceso: 1,
      resueltos: 6,
      cancelados: 1,
      total_tecnicos: 3,
      total_dispositivos: 10,
    },
    mantenimientosRecientes: {
      count: 1,
      results: [{ id: 1, fecha: '2026-08-14', estado: 'pendiente' }],
    },
    espaciosDestacados: {
      count: 3,
      results: [
        { id: 1, codigo_espacio: 'A-101', cantidad_equipos: 2 },
        { id: 2, codigo_espacio: 'LAB-02', cantidad_equipos: 6 },
        { id: 3, codigo_espacio: 'B-201', cantidad_equipos: 4 },
      ],
    },
  },
  failed: [],
};

const mountComposable = (service, role = 'admin') => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  const authStore = useAuthStore();
  authStore.user = { id: 1, nombre: 'Leonardo', rol: role };

  const wrapper = mount(defineComponent({
    setup() {
      state = useDashboard(service);
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });

  return { state, wrapper };
};

describe('useDashboard', () => {
  let service;

  beforeEach(() => {
    service = {
      obtenerResumen: vi.fn().mockResolvedValue(dashboardResponse),
    };
  });

  it('carga y calcula los indicadores operativos', async () => {
    const { state } = mountComposable(service);
    await flushPromises();

    expect(service.obtenerResumen).toHaveBeenCalledOnce();
    expect(state.firstName.value).toBe('Leonardo');
    expect(state.equipmentOperationalRate.value).toBe(70);
    expect(state.openMaintenance.value).toBe(3);
    expect(state.maintenanceResolutionRate.value).toBe(60);
    expect(state.recentMaintenance.value).toHaveLength(1);
  });

  it('ordena los espacios por cantidad de equipos', async () => {
    const { state } = mountComposable(service);
    await flushPromises();

    expect(state.topSpaces.value.map((space) => space.codigo_espacio)).toEqual([
      'LAB-02',
      'B-201',
      'A-101',
    ]);
  });

  it('conserva los datos disponibles cuando una fuente falla', async () => {
    service.obtenerResumen.mockResolvedValue({
      ...dashboardResponse,
      failed: ['usuarios'],
    });
    const { state } = mountComposable(service);
    await flushPromises();

    expect(state.equipmentStats.total).toBe(10);
    expect(state.warning.value).toContain('Algunos indicadores');
  });

  it('no solicita métricas restringidas para otros roles', async () => {
    const { state } = mountComposable(service, 'docente');
    await flushPromises();

    expect(state.canViewOperations.value).toBe(false);
    expect(service.obtenerResumen).not.toHaveBeenCalled();
  });
});
