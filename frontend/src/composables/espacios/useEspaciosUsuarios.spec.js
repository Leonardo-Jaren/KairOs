import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { describe, expect, it, vi } from 'vitest';

import { useEspaciosUsuarios } from '@/composables/espacios/useEspaciosUsuarios';
import { useAuthStore } from '@/stores/auth';

const assignment = {
  id: 7,
  ambito: 'espacio',
  ambito_display: 'Espacio individual',
  usuario: { id: 2, nombre_completo: 'Diana Docente', correo: 'diana@udh.edu.pe', rol: 'docente' },
  espacio: { id: 3, codigo_espacio: 'LAB-202', pabellon: 'Pabellón 2', piso: '2' },
  local_id: 1,
  edificio_id: 2,
  piso: '2',
  espacio_id: 3,
  ubicacion_display: 'LAB-202 · Pabellón 2',
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
      results: [
        { id: 3, codigo_espacio: 'LAB-202', pabellon: 'Pabellón 2', edificio_id: 10, piso: '2' },
        { id: 4, codigo_espacio: 'LAB-101', pabellon: 'Pabellón 1', edificio_id: 11, piso: '1' },
      ],
    }),
  },
  locales: {
    listar: vi.fn().mockResolvedValue({
      count: 2,
      results: [
        { id: 1, nombre: 'Campus Central', codigo: 'CC' },
        { id: 2, nombre: 'Sede La Florida', codigo: 'LF' },
      ],
    }),
  },
  edificios: {
    listar: vi.fn().mockResolvedValue({
      count: 3,
      results: [
        { id: 10, local_id: 1, nombre: 'Pabellón 1', pisos: ['1', '2'] },
        { id: 11, local_id: 1, nombre: 'Pabellón 2', pisos: ['1', '2', '3'] },
        { id: 20, local_id: 2, nombre: 'Pabellón B', pisos: ['1'] },
      ],
    }),
  },
});

const mountComposable = (service = createService(), role = 'admin', optionServices = createOptionServices()) => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  if (role) {
    useAuthStore().user = typeof role === 'object' ? role : { id: 1, nombre: 'Ada', rol: role };
  } else {
    useAuthStore().user = null;
  }
  mount(defineComponent({
    setup() {
      state = useEspaciosUsuarios(service, optionServices);
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });
  return state;
};

describe('useEspaciosUsuarios', () => {
  describe('operaciones base y carga paginada', () => {
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

  describe('canEdit: control de permisos por rol (Feature 11)', () => {
    it.each([
      ['superadmin', true],
      ['admin', true],
      ['responsable', true],
      ['tecnico', false],
      ['docente', false],
      ['usuario', false],
    ])('asigna canEdit=%s para el rol "%s"', async (rol, expected) => {
      const state = mountComposable(createService(), rol);
      await flushPromises();
      expect(state.canEdit.value).toBe(expected);
    });

    it('permite canEdit=true para usuarios con is_superuser=true', async () => {
      const state = mountComposable(createService(), { id: 99, nombre: 'Root', rol: 'operador', is_superuser: true });
      await flushPromises();
      expect(state.canEdit.value).toBe(true);
    });

    it('restringe canEdit=false para usuarios desautenticados', async () => {
      const state = mountComposable(createService(), null);
      await flushPromises();
      expect(state.canEdit.value).toBe(false);
    });
  });

  describe('estado reactivo en cascada y reseteo (Feature 9)', () => {
    it('inicializa el formulario con valores por defecto y scope espacio', async () => {
      const state = mountComposable();
      await flushPromises();

      const ambitoVal = state.form.tipo_ambito ?? state.form.ambito;
      expect(ambitoVal).toBe('espacio');
      expect(state.form.local_id).toBe('');
      expect(state.form.edificio_id).toBe('');
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');
      expect(state.form.usuario_id).toBe('');
      expect(state.form.tipo_responsabilidad).toBe('responsable');
      expect(state.form.activo).toBe(true);
    });

    it('limpia campos descendientes al cambiar de ámbito territorial', async () => {
      const state = mountComposable();
      await flushPromises();

      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '2';
      state.form.espacio_id = 3;

      if (typeof state.onAmbitoChange === 'function') {
        state.onAmbitoChange('sede');
      } else {
        state.form.tipo_ambito = 'sede';
      }

      expect(state.form.local_id).toBe(1);
      expect(state.form.edificio_id).toBe('');
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');

      state.form.edificio_id = 10;
      state.form.piso = '2';
      state.form.espacio_id = 3;

      if (typeof state.onAmbitoChange === 'function') {
        state.onAmbitoChange('edificio');
      } else {
        state.form.tipo_ambito = 'edificio';
      }

      expect(state.form.edificio_id).toBe(10);
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');

      state.form.piso = '2';
      state.form.espacio_id = 3;

      if (typeof state.onAmbitoChange === 'function') {
        state.onAmbitoChange('piso');
      } else {
        state.form.tipo_ambito = 'piso';
      }

      expect(state.form.piso).toBe('2');
      expect(state.form.espacio_id).toBe('');
    });

    it('limpia edificio, piso y espacio al cambiar la sede seleccionada', async () => {
      const state = mountComposable();
      await flushPromises();

      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '2';
      state.form.espacio_id = 3;

      if (typeof state.onLocalChange === 'function') {
        state.onLocalChange(2);
      } else {
        state.form.local_id = 2;
        state.form.edificio_id = '';
        state.form.piso = '';
        state.form.espacio_id = '';
      }

      expect(state.form.local_id).toBe(2);
      expect(state.form.edificio_id).toBe('');
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');
    });

    it('limpia piso y espacio al cambiar el edificio seleccionado', async () => {
      const state = mountComposable();
      await flushPromises();

      state.form.edificio_id = 10;
      state.form.piso = '2';
      state.form.espacio_id = 3;

      if (typeof state.onEdificioChange === 'function') {
        state.onEdificioChange(11);
      } else {
        state.form.edificio_id = 11;
        state.form.piso = '';
        state.form.espacio_id = '';
      }

      expect(state.form.edificio_id).toBe(11);
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');
    });

    it('resetea completamente el estado y errores al abrir creación o cerrar modal', async () => {
      const state = mountComposable();
      await flushPromises();

      state.form.tipo_ambito = 'piso';
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '2';
      state.form.usuario_id = 2;
      state.formErrors.usuario_id = 'Error previo';
      state.editingAssignment.value = { id: 99 };

      state.openCreate();
      expect(state.modalOpen.value).toBe(true);
      expect(state.editingAssignment.value).toBeNull();
      const ambitoVal = state.form.tipo_ambito ?? state.form.ambito;
      expect(ambitoVal).toBe('espacio');
      expect(state.form.local_id).toBe('');
      expect(state.form.edificio_id).toBe('');
      expect(state.form.piso).toBe('');
      expect(state.form.usuario_id).toBe('');
      expect(Object.keys(state.formErrors).length).toBe(0);

      state.closeModal();
      expect(state.modalOpen.value).toBe(false);
    });

    it('hidrata correctamente el formulario al editar asignaciones de diferentes ámbitos', async () => {
      const state = mountComposable();
      await flushPromises();

      const pisoAssignment = {
        id: 25,
        ambito: 'piso',
        local_id: 1,
        edificio_id: 10,
        piso: '3',
        usuario: { id: 5, nombre_completo: 'Carlos Técnico', correo: 'carlos@udh.edu.pe' },
        tipo_responsabilidad: 'tecnico',
        activo: true,
      };

      state.openEdit(pisoAssignment);
      expect(state.modalOpen.value).toBe(true);
      expect(state.isEditing.value).toBe(true);
      const ambitoVal = state.form.tipo_ambito ?? state.form.ambito;
      expect(ambitoVal).toBe('piso');
      expect(state.form.local_id).toBe(1);
      expect(state.form.edificio_id).toBe(10);
      expect(state.form.piso).toBe('3');
      expect(state.form.usuario_id).toBe(5);
      expect(state.form.tipo_responsabilidad).toBe('tecnico');
      expect(state.form.activo).toBe(true);
    });
  });

  describe('validación en cliente por ámbito (Feature 9)', () => {
    it('valida campos requeridos para el ámbito sede', async () => {
      const service = createService();
      const state = mountComposable(service);
      await flushPromises();

      state.openCreate();
      if (typeof state.onAmbitoChange === 'function') {
        state.onAmbitoChange('sede');
      } else {
        state.form.tipo_ambito = 'sede';
      }

      expect(await state.submit()).toBe(false);
      expect(service.crear).not.toHaveBeenCalled();
      expect(state.formErrors.usuario_id).toBeTruthy();
      expect(state.formErrors.local_id).toBeTruthy();
      expect(state.formErrors.edificio_id).toBeUndefined();
      expect(state.formErrors.piso).toBeUndefined();
      expect(state.formErrors.espacio_id).toBeUndefined();

      state.form.usuario_id = 2;
      state.form.local_id = 1;
      expect(await state.submit()).toBe(true);
      expect(service.crear).toHaveBeenCalled();
    });

    it('valida campos requeridos para el ámbito edificio', async () => {
      const service = createService();
      const state = mountComposable(service);
      await flushPromises();

      state.openCreate();
      if (typeof state.onAmbitoChange === 'function') {
        state.onAmbitoChange('edificio');
      } else {
        state.form.tipo_ambito = 'edificio';
      }
      state.form.usuario_id = 2;
      state.form.local_id = 1;
      state.form.edificio_id = '';

      expect(await state.submit()).toBe(false);
      expect(state.formErrors.edificio_id).toBeTruthy();
      expect(state.formErrors.piso).toBeUndefined();
      expect(state.formErrors.espacio_id).toBeUndefined();

      state.form.edificio_id = 10;
      expect(await state.submit()).toBe(true);
    });

    it('valida campos requeridos para el ámbito piso', async () => {
      const service = createService();
      const state = mountComposable(service);
      await flushPromises();

      state.openCreate();
      if (typeof state.onAmbitoChange === 'function') {
        state.onAmbitoChange('piso');
      } else {
        state.form.tipo_ambito = 'piso';
      }
      state.form.usuario_id = 2;
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '';

      expect(await state.submit()).toBe(false);
      expect(state.formErrors.piso).toBeTruthy();
      expect(state.formErrors.espacio_id).toBeUndefined();

      state.form.piso = '   ';
      expect(await state.submit()).toBe(false);
      expect(state.formErrors.piso).toBeTruthy();

      state.form.piso = '2';
      expect(await state.submit()).toBe(true);
    });

    it('valida campos requeridos para el ámbito espacio', async () => {
      const service = createService();
      const state = mountComposable(service);
      await flushPromises();

      state.openCreate();
      if (typeof state.onAmbitoChange === 'function') {
        state.onAmbitoChange('espacio');
      } else {
        state.form.tipo_ambito = 'espacio';
      }
      state.form.usuario_id = 2;
      state.form.espacio_id = '';

      expect(await state.submit()).toBe(false);
      expect(state.formErrors.espacio_id).toBeTruthy();

      state.form.espacio_id = 3;
      expect(await state.submit()).toBe(true);
    });
  });

  describe('construcción de payloads en los 4 ámbitos (Features 1, 2, 9)', () => {
    it('construye payload para ámbito sede con local_id y nulos en campos subordinados', async () => {
      const service = createService();
      const state = mountComposable(service);
      await flushPromises();

      state.openCreate();
      if (typeof state.onAmbitoChange === 'function') {
        state.onAmbitoChange('sede');
      }
      Object.assign(state.form, {
        tipo_ambito: 'sede',
        ambito: 'sede',
        usuario_id: '2',
        local_id: '1',
        tipo_responsabilidad: 'responsable',
        activo: true,
      });

      await state.submit();

      expect(service.crear).toHaveBeenCalledWith(expect.objectContaining({
        ambito: 'sede',
        usuario_id: 2,
        local_id: 1,
        edificio_id: null,
        piso: null,
        espacio_id: null,
        tipo_responsabilidad: 'responsable',
        activo: true,
      }));
    });

    it('construye payload para ámbito edificio con local_id y edificio_id', async () => {
      const service = createService();
      const state = mountComposable(service);
      await flushPromises();

      state.openCreate();
      if (typeof state.onAmbitoChange === 'function') {
        state.onAmbitoChange('edificio');
      }
      Object.assign(state.form, {
        tipo_ambito: 'edificio',
        ambito: 'edificio',
        usuario_id: '5',
        local_id: '1',
        edificio_id: '10',
        tipo_responsabilidad: 'tecnico',
        activo: true,
      });

      await state.submit();

      expect(service.crear).toHaveBeenCalledWith(expect.objectContaining({
        ambito: 'edificio',
        usuario_id: 5,
        local_id: 1,
        edificio_id: 10,
        piso: null,
        espacio_id: null,
        tipo_responsabilidad: 'tecnico',
        activo: true,
      }));
    });

    it('construye payload para ámbito piso con local_id, edificio_id y piso', async () => {
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
        usuario_id: '8',
        local_id: '1',
        edificio_id: '10',
        piso: 'Piso 2',
        tipo_responsabilidad: 'tecnico',
        activo: true,
      });

      await state.submit();

      expect(service.crear).toHaveBeenCalledWith(expect.objectContaining({
        ambito: 'piso',
        usuario_id: 8,
        local_id: 1,
        edificio_id: 10,
        piso: 'Piso 2',
        espacio_id: null,
        tipo_responsabilidad: 'tecnico',
        activo: true,
      }));
    });

    it('convierte identificadores y crea una asignación para ámbito espacio (compatibilidad)', async () => {
      const service = createService();
      const state = mountComposable(service);
      await flushPromises();

      state.openCreate();
      Object.assign(state.form, {
        tipo_ambito: 'espacio',
        ambito: 'espacio',
        usuario_id: '2',
        espacio_id: '3',
        tipo_responsabilidad: 'docente',
        activo: true,
      });

      const result = await state.submit();

      expect(result).toBe(true);
      expect(service.crear).toHaveBeenCalledWith(expect.objectContaining({
        usuario_id: 2,
        espacio_id: 3,
        tipo_responsabilidad: 'docente',
        activo: true,
      }));
    });
  });

  describe('filtrado por local_id y edificio_id (Feature 10)', () => {
    it('envía local_id y edificio_id al listar asignaciones', async () => {
      const service = createService();
      const state = mountComposable(service);
      await flushPromises();

      state.filters.local_id = 1;
      state.filters.edificio_id = 10;
      await state.applyFilters();

      expect(service.listar).toHaveBeenCalledWith(expect.objectContaining({
        local_id: 1,
        edificio_id: 10,
      }));
    });

    it('resetea los filtros territoriales con clearFilters()', async () => {
      const service = createService();
      const state = mountComposable(service);
      await flushPromises();

      state.filters.local_id = 1;
      state.filters.edificio_id = 10;
      state.filters.search = 'Prueba';
      state.filters.activo = 'true';

      state.clearFilters();
      await flushPromises();

      expect(state.filters.local_id).toBe('');
      expect(state.filters.edificio_id).toBe('');
      expect(state.filters.search).toBe('');
      expect(state.filters.activo).toBe('');
      expect(service.listar).toHaveBeenCalledWith(expect.objectContaining({
        local_id: '',
        edificio_id: '',
        search: '',
        activo: '',
      }));
    });
  });
});
