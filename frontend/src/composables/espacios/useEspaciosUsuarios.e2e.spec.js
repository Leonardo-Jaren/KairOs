import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { describe, expect, it, vi } from 'vitest';

import { useEspaciosUsuarios } from '@/composables/espacios/useEspaciosUsuarios';
import { useAuthStore } from '@/stores/auth';

const assignmentPiso = {
  id: 10,
  ambito: 'piso',
  ambito_display: 'Piso',
  usuario: { id: 5, nombre_completo: 'Tomás Técnico', correo: 'tomas@udh.edu.pe', rol: 'tecnico' },
  local_id: 1,
  local: { id: 1, nombre: 'Campus Central' },
  edificio_id: 2,
  edificio: { id: 2, nombre: 'Pabellón A' },
  piso: '2',
  espacio_id: null,
  espacio: null,
  ubicacion_display: 'Pabellón A · Piso 2',
  tipo_responsabilidad: 'tecnico',
  tipo_responsabilidad_display: 'Soporte técnico',
  activo: true,
};

const createService = () => ({
  listar: vi.fn().mockResolvedValue({ count: 1, results: [assignmentPiso] }),
  crear: vi.fn().mockResolvedValue(assignmentPiso),
  actualizar: vi.fn().mockResolvedValue(assignmentPiso),
  eliminar: vi.fn().mockResolvedValue(undefined),
});

const createOptionServices = () => ({
  usuarios: {
    listar: vi.fn().mockResolvedValue({
      count: 5,
      results: [{ id: 5, nombre_completo: 'Tomás Técnico', correo: 'tomas@udh.edu.pe' }],
    }),
  },
  espacios: {
    listar: vi.fn().mockResolvedValue({
      count: 2,
      results: [{ id: 3, codigo_espacio: 'LAB-201', pabellon: 'Pabellón A' }],
    }),
  },
  locales: {
    listar: vi.fn().mockResolvedValue({
      count: 1,
      results: [{ id: 1, nombre: 'Campus Central' }],
    }),
  },
  edificios: {
    listar: vi.fn().mockResolvedValue({
      count: 1,
      results: [{ id: 2, nombre: 'Pabellón A', local_id: 1 }],
    }),
  },
});

const mountComposable = (service = createService(), user = { id: 1, nombre: 'Ada', rol: 'admin' }) => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  useAuthStore().user = user;
  mount(defineComponent({
    setup() {
      state = useEspaciosUsuarios(service, createOptionServices());
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });
  return state;
};

describe('E2E Frontend: useEspaciosUsuarios (Features 9, 10, 11)', () => {
  it('Feature 11: permite canEdit=true para administradores, superadmin y responsables', async () => {
    const stateAdmin = mountComposable(createService(), { id: 1, rol: 'admin' });
    const stateSuper = mountComposable(createService(), { id: 2, rol: 'superadmin' });
    const stateResp = mountComposable(createService(), { id: 3, rol: 'responsable' });
    await flushPromises();

    expect(stateAdmin.canEdit.value).toBe(true);
    expect(stateSuper.canEdit.value).toBe(true);
    expect(stateResp.canEdit.value).toBe(true);
  });

  it('Feature 11: restringe canEdit=false para técnicos y docentes', async () => {
    const stateTecnico = mountComposable(createService(), { id: 2, rol: 'tecnico' });
    await flushPromises();
    expect(stateTecnico.canEdit.value).toBe(false);

    const stateDocente = mountComposable(createService(), { id: 3, rol: 'docente' });
    await flushPromises();
    expect(stateDocente.canEdit.value).toBe(false);
  });

  it('Feature 10: carga asignaciones y expone tabla paginada con formato de ubicación compuesto', async () => {
    const service = createService();
    const state = mountComposable(service);
    await flushPromises();

    expect(state.asignaciones.value).toHaveLength(1);
    const item = state.asignaciones.value[0];
    expect(item.usuario.nombre_completo).toBe('Tomás Técnico');
    expect(item.ubicacion_display).toBe('Pabellón A · Piso 2');
    expect(item.edificio?.nombre || item.espacio?.pabellon || item.ubicacion_display).toBeTruthy();
  });

  it('Feature 9: modal abre con formulario inicializado y resetea estado', async () => {
    const state = mountComposable();
    await flushPromises();

    state.openCreate();
    expect(state.modalOpen.value).toBe(true);
    expect(state.editingAssignment.value).toBeNull();
    expect(state.isEditing.value).toBe(false);
  });

  it('Feature 9 & 1: flujo E2E de creación en ámbito piso con recarga de lista', async () => {
    const service = createService();
    const state = mountComposable(service);
    await flushPromises();

    state.openCreate();
    if (typeof state.onAmbitoChange === 'function') {
      state.onAmbitoChange('piso');
    }
    Object.assign(state.form, {
      tipo_ambito: 'piso',
      ambito: 'piso',
      local_id: '1',
      edificio_id: '2',
      piso: '2',
      usuario_id: '5',
      tipo_responsabilidad: 'tecnico',
      activo: true,
    });

    const success = await state.submit();
    expect(success).toBe(true);
    expect(service.crear).toHaveBeenCalledWith(expect.objectContaining({
      ambito: 'piso',
      local_id: 1,
      edificio_id: 2,
      piso: '2',
      usuario_id: 5,
      espacio_id: null,
      tipo_responsabilidad: 'tecnico',
      activo: true,
    }));
    expect(state.modalOpen.value).toBe(false);
    expect(service.listar).toHaveBeenCalledTimes(2);
  });

  it('Feature 10: flujo E2E de filtrado territorial y limpieza', async () => {
    const service = createService();
    const state = mountComposable(service);
    await flushPromises();

    state.filters.local_id = 1;
    state.filters.edificio_id = 2;
    await state.applyFilters();

    expect(service.listar).toHaveBeenCalledWith(expect.objectContaining({
      local_id: 1,
      edificio_id: 2,
    }));

    state.clearFilters();
    await flushPromises();

    expect(state.filters.local_id).toBe('');
    expect(state.filters.edificio_id).toBe('');
  });
});
