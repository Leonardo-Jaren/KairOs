import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { describe, expect, it, vi } from 'vitest';

import { useEspaciosUsuarios } from '@/composables/espacios/useEspaciosUsuarios';
import { useAuthStore } from '@/stores/auth';

const assignment = {
  id: 7,
  usuario: { id: 2, nombre_completo: 'Diana Docente', correo: 'diana@udh.edu.pe', rol: 'docente' },
  espacio: { id: 3, codigo_espacio: 'LAB-202', pabellon: 'Pabellón 2', piso: '2' },
  tipo_responsabilidad: 'docente',
  tipo_responsabilidad_display: 'Docente asignado',
  activo: true,
};

const createService = () => ({
  listar: vi.fn().mockResolvedValue({ count: 1, results: [assignment] }),
  crear: vi.fn().mockResolvedValue(assignment),
  actualizar: vi.fn().mockResolvedValue(assignment),
  eliminar: vi.fn().mockResolvedValue(undefined),
});

const createOptionServices = () => ({
  usuarios: {
    listar: vi.fn().mockResolvedValue({
      count: 12,
      results: [{ id: 2, nombre_completo: 'Diana Docente', correo: 'diana@udh.edu.pe' }],
    }),
  },
  espacios: {
    listar: vi.fn().mockResolvedValue({
      count: 11,
      results: [{ id: 3, codigo_espacio: 'LAB-202', pabellon: 'Pabellón 2' }],
    }),
  },
});

const mountComposable = (service, role = 'admin', optionServices = createOptionServices()) => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  useAuthStore().user = { id: 1, nombre: 'Ada', rol: role };
  mount(defineComponent({
    setup() {
      state = useEspaciosUsuarios(service, optionServices);
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });
  return state;
};

describe('useEspaciosUsuarios', () => {
  it('carga las asignaciones sin descargar catálogos completos', async () => {
    const service = createService();
    const optionServices = createOptionServices();
    const state = mountComposable(service, 'admin', optionServices);
    await flushPromises();

    expect(state.asignaciones.value).toHaveLength(1);
    expect(state.uniqueSpaces.value).toBe(1);
    expect(optionServices.usuarios.listar).not.toHaveBeenCalled();
    expect(optionServices.espacios.listar).not.toHaveBeenCalled();
  });

  it('carga usuarios y espacios en páginas remotas de diez registros', async () => {
    const optionServices = createOptionServices();
    const state = mountComposable(createService(), 'admin', optionServices);
    await flushPromises();

    const users = await state.loadUserOptions({ page: 2, pageSize: 10, search: 'Diana' });
    const spaces = await state.loadSpaceOptions({ page: 1, pageSize: 10, search: 'LAB' });

    expect(optionServices.usuarios.listar).toHaveBeenCalledWith({
      page: 2,
      page_size: 10,
      search: 'Diana',
      activo: 'true',
    });
    expect(optionServices.espacios.listar).toHaveBeenCalledWith({
      page: 1,
      page_size: 10,
      search: 'LAB',
      activo: 'true',
    });
    expect(users.total).toBe(12);
    expect(users.options[0].label).toContain('diana@udh.edu.pe');
    expect(spaces.total).toBe(11);
  });

  it('expone escritura solamente para administradores', async () => {
    const optionServices = createOptionServices();
    const state = mountComposable(createService(), 'tecnico', optionServices);
    await flushPromises();

    expect(state.canEdit.value).toBe(false);
    expect(optionServices.usuarios.listar).not.toHaveBeenCalled();
  });

  it('valida que usuario y espacio sean obligatorios', async () => {
    const service = createService();
    const state = mountComposable(service);
    await flushPromises();

    expect(await state.submit()).toBe(false);
    expect(service.crear).not.toHaveBeenCalled();
    expect(state.formErrors.usuario_id).toBeTruthy();
    expect(state.formErrors.espacio_id).toBeTruthy();
  });

  it('convierte identificadores y crea una asignación', async () => {
    const service = createService();
    const state = mountComposable(service);
    await flushPromises();
    state.openCreate();
    Object.assign(state.form, {
      usuario_id: '2',
      espacio_id: '3',
      tipo_responsabilidad: 'docente',
      activo: true,
    });

    const result = await state.submit();

    expect(result).toBe(true);
    expect(service.crear).toHaveBeenCalledWith({
      usuario_id: 2,
      espacio_id: 3,
      tipo_responsabilidad: 'docente',
      activo: true,
    });
  });

  it('conserva la opción seleccionada al editar una asignación', async () => {
    const state = mountComposable(createService());
    await flushPromises();

    state.openEdit(assignment);

    expect(state.selectedUserOption.value).toEqual({
      value: 2,
      label: 'Diana Docente · diana@udh.edu.pe',
    });
    expect(state.selectedSpaceOption.value.label).toContain('LAB-202');
  });

  it('elimina la asignación confirmada y recarga la lista', async () => {
    const service = createService();
    const state = mountComposable(service);
    await flushPromises();
    state.askDelete(assignment);

    await state.confirmDelete();

    expect(service.eliminar).toHaveBeenCalledWith(7);
    expect(service.listar).toHaveBeenCalledTimes(2);
    expect(state.deleteModalOpen.value).toBe(false);
  });
});
