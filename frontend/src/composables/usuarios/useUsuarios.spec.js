import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useUsuarios } from '@/composables/usuarios/useUsuarios';
import { useAuthStore } from '@/stores/auth';

const usersResponse = {
  count: 1,
  results: [{
    id: 1,
    username: 'docente',
    correo: 'docente@udh.edu.pe',
    nombre: 'Diana',
    apellido: 'Docente',
    nombre_completo: 'Diana Docente',
    dni: '12345678',
    rol: 'docente',
    is_active: true,
  }],
};

const createService = () => ({
  listar: vi.fn().mockResolvedValue(usersResponse),
  obtenerEstadisticas: vi.fn().mockResolvedValue({
    total: 1,
    activos: 1,
    administradores: 0,
    tecnicos: 0,
    docentes: 1,
  }),
  crear: vi.fn().mockResolvedValue(usersResponse.results[0]),
  actualizar: vi.fn().mockResolvedValue(usersResponse.results[0]),
  desactivar: vi.fn().mockResolvedValue(undefined),
});

const mountComposable = (service, role = 'admin') => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  const authStore = useAuthStore();
  authStore.user = { id: 99, nombre: 'Ada', rol: role };

  const wrapper = mount(defineComponent({
    setup() {
      state = useUsuarios(service);
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });

  return { state, wrapper };
};

describe('useUsuarios', () => {
  let service;

  beforeEach(() => {
    service = createService();
  });

  it('carga usuarios, paginación e indicadores al montar', async () => {
    const { state } = mountComposable(service);
    await flushPromises();

    expect(service.listar).toHaveBeenCalledOnce();
    expect(service.obtenerEstadisticas).toHaveBeenCalledOnce();
    expect(state.usuarios.value).toHaveLength(1);
    expect(state.pagination.total).toBe(1);
    expect(state.stats.docentes).toBe(1);
  });

  it('limita los roles disponibles para un técnico', async () => {
    const { state } = mountComposable(service, 'tecnico');
    await flushPromises();

    expect(state.canManageAll.value).toBe(false);
    expect(state.availableRoleOptions.value).toEqual([
      { value: 'docente', label: 'Docente' },
    ]);
  });

  it('valida el formulario antes de crear', async () => {
    const { state } = mountComposable(service);
    await flushPromises();

    const result = await state.submit();

    expect(result).toBe(false);
    expect(service.crear).not.toHaveBeenCalled();
    expect(state.formErrors.nombre).toBeTruthy();
    expect(state.formErrors.correo).toBeTruthy();
  });

  it('crea un usuario válido y recarga la información', async () => {
    const { state } = mountComposable(service);
    await flushPromises();
    state.openCreate();
    Object.assign(state.form, {
      username: 'docente',
      correo: 'docente@udh.edu.pe',
      nombre: 'Diana',
      apellido: 'Docente',
      dni: '12345678',
      rol: 'docente',
      password: 'TeacherPass123',
      is_active: true,
    });

    const result = await state.submit();

    expect(result).toBe(true);
    expect(service.crear).toHaveBeenCalledWith(expect.objectContaining({
      correo: 'docente@udh.edu.pe',
      rol: 'docente',
    }));
    expect(state.toast.type).toBe('success');
    expect(state.modalOpen.value).toBe(false);
  });

  it('actualiza el usuario seleccionado sin exigir contraseña', async () => {
    const { state } = mountComposable(service);
    await flushPromises();
    state.openEdit(usersResponse.results[0]);

    const result = await state.submit();

    expect(result).toBe(true);
    expect(service.actualizar).toHaveBeenCalledWith(
      1,
      expect.not.objectContaining({ password: expect.anything() }),
    );
  });

  it('muestra el error entregado por la API', async () => {
    service.crear.mockRejectedValue({ response: { data: { correo: ['Correo duplicado.'] } } });
    const { state } = mountComposable(service);
    await flushPromises();
    state.openCreate();
    Object.assign(state.form, {
      username: 'docente',
      correo: 'docente@udh.edu.pe',
      nombre: 'Diana',
      rol: 'docente',
      password: 'TeacherPass123',
    });

    await state.submit();

    expect(state.toast.type).toBe('error');
    expect(state.toast.message).toBe('Correo duplicado.');
  });
});
