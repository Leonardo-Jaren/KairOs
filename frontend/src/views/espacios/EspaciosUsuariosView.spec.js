import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import EspaciosUsuariosView from '@/views/espacios/EspaciosUsuariosView.vue';
import espaciosUsuariosService from '@/services/espacios-usuarios.service';
import localesService from '@/services/locales.service';
import edificiosService from '@/services/edificios.service';
import espaciosService from '@/services/espacios.service';
import usuariosService from '@/services/usuarios.service';
import { useAuthStore } from '@/stores/auth';

// Mock de todos los servicios API utilizados por el composable y la vista
vi.mock('@/services/espacios-usuarios.service', () => ({
  default: {
    listar: vi.fn(),
    crear: vi.fn(),
    actualizar: vi.fn(),
    eliminar: vi.fn(),
    obtenerOpciones: vi.fn(),
  },
}));

vi.mock('@/services/locales.service', () => ({
  default: {
    listar: vi.fn().mockResolvedValue({
      count: 2,
      results: [
        { id: 1, nombre: 'Sede Norte', codigo: 'SN', ciudad: 'Huánuco' },
        { id: 2, nombre: 'Sede Sur', codigo: 'SS', ciudad: 'Lima' },
      ],
    }),
  },
}));

vi.mock('@/services/edificios.service', () => ({
  default: {
    listar: vi.fn().mockResolvedValue({
      count: 2,
      results: [
        { id: 10, local_id: 1, nombre: 'Pabellón A', pisos: ['1', '2'] },
        { id: 20, local_id: 2, nombre: 'Pabellón B', pisos: ['PB', '1'] },
      ],
    }),
  },
}));

vi.mock('@/services/espacios.service', () => ({
  default: {
    listar: vi.fn().mockResolvedValue({
      count: 1,
      results: [
        { id: 101, codigo_espacio: 'LAB-101', pabellon: 'Pabellón A', piso: '1', local_id: 1, edificio_id: 10 },
      ],
    }),
  },
}));

vi.mock('@/services/usuarios.service', () => ({
  default: {
    listar: vi.fn().mockResolvedValue({
      count: 1,
      results: [
        { id: 5, nombre_completo: 'Carlos Técnico', correo: 'carlos@kairos.edu' },
      ],
    }),
  },
}));

const setupTestEnvironment = (role = 'responsable') => {
  const pinia = createPinia();
  setActivePinia(pinia);
  const authStore = useAuthStore();
  authStore.user = {
    id: 1,
    nombre: 'Usuario Prueba',
    rol: role,
    is_superuser: role === 'superadmin',
  };
  return pinia;
};

const mountView = (pinia) => {
  return mount(EspaciosUsuariosView, {
    global: {
      plugins: [pinia],
      stubs: {
        Teleport: true,
        Transition: false,
      },
    },
  });
};

describe('EspaciosUsuariosView — Adversarial & Stress Testing (Milestone 3)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('1. Filas de datos patológicas y funciones de formateo', () => {
    it('renderiza correctamente fila con ámbito="sede", espacio=null, edificio=null, piso=null, local={id: 1, nombre: "Sede Norte"}', async () => {
      const pinia = setupTestEnvironment('responsable');
      const rowSede = {
        id: 101,
        ambito: 'sede',
        espacio: null,
        edificio: null,
        piso: null,
        local: { id: 1, nombre: 'Sede Norte' },
        usuario: { id: 10, nombre_completo: 'Laura Responsable', correo: 'laura@kairos.edu' },
        tipo_responsabilidad: 'responsable',
        activo: true,
      };

      espaciosUsuariosService.listar.mockResolvedValueOnce({
        count: 1,
        results: [rowSede],
      });

      const wrapper = mountView(pinia);
      await flushPromises();

      const text = wrapper.text();
      // Formato principal debe ser el nombre del local
      expect(text).toContain('Sede Norte');
      // Formato secundario de sede sin ciudad ni codigo debe caer en fallback 'Sede principal'
      expect(text).toContain('Sede principal');
      // Badge de ámbito
      expect(text).toContain('Sede');
      // Usuario
      expect(text).toContain('Laura Responsable');
      expect(text).toContain('laura@kairos.edu');
    });

    it('renderiza correctamente fila con ámbito="edificio", espacio=null, edificio={id: 2, nombre: "Pabellón B"}, local=null', async () => {
      const pinia = setupTestEnvironment('responsable');
      const rowEdificio = {
        id: 102,
        ambito: 'edificio',
        espacio: null,
        edificio: { id: 2, nombre: 'Pabellón B' },
        local: null,
        usuario: { id: 12, nombre_completo: 'Marcos Pabellón', correo: 'marcos@kairos.edu' },
        tipo_responsabilidad: 'tecnico',
        activo: true,
      };

      espaciosUsuariosService.listar.mockResolvedValueOnce({
        count: 1,
        results: [rowEdificio],
      });

      const wrapper = mountView(pinia);
      await flushPromises();

      const text = wrapper.text();
      // Ubicación principal: nombre del edificio
      expect(text).toContain('Pabellón B');
      // Ubicación secundaria sin local ni codigo: fallback 'Edificio completo'
      expect(text).toContain('Edificio completo');
      // Badge de ámbito
      expect(text).toContain('Pabellón');
    });

    it('renderiza correctamente fila con ámbito="piso", piso="PB", edificio=null, espacio=null, local=null', async () => {
      const pinia = setupTestEnvironment('responsable');
      const rowPiso = {
        id: 103,
        ambito: 'piso',
        piso: 'PB',
        edificio: null,
        espacio: null,
        local: null,
        usuario: { id: 15, nombre_completo: 'Patricia Planta', correo: 'patricia@kairos.edu' },
        tipo_responsabilidad: 'tecnico',
        activo: true,
      };

      espaciosUsuariosService.listar.mockResolvedValueOnce({
        count: 1,
        results: [rowPiso],
      });

      const wrapper = mountView(pinia);
      await flushPromises();

      const text = wrapper.text();
      // Ubicación principal con edificio nulo: 'Pabellón · Piso PB'
      expect(text).toContain('Pabellón · Piso PB');
      // Ubicación secundaria con local nulo: fallback 'Nivel de planta'
      expect(text).toContain('Nivel de planta');
      // Badge de ámbito
      expect(text).toContain('Piso');
    });

    it('maneja fila completamente malformada con todos los campos en null sin arrojar excepciones', async () => {
      const pinia = setupTestEnvironment('responsable');
      const rowAllNulls = {
        id: 999,
        ambito: null,
        ambito_display: null,
        espacio: null,
        edificio: null,
        local: null,
        piso: null,
        nombre_ambito: null,
        ubicacion_display: null,
        usuario: null,
        tipo_responsabilidad: null,
        activo: null,
      };

      espaciosUsuariosService.listar.mockResolvedValueOnce({
        count: 1,
        results: [rowAllNulls],
      });

      const wrapper = mountView(pinia);
      await flushPromises();

      const text = wrapper.text();
      // Usuario nulo -> fallback 'Usuario sin nombre' e inicial 'U'
      expect(text).toContain('Usuario sin nombre');
      expect(text).toContain('U');
      // Ámbito nulo -> fallback 'Ámbito'
      expect(text).toContain('Ámbito');
      // Ubicación principal con ámbito nulo/espacio nulo -> fallback 'Espacio individual'
      expect(text).toContain('Espacio individual');
      // Estado nulo -> fallback 'Inactiva'
      expect(text).toContain('Inactiva');

      // Verificar invocación directa de métodos de formateo para verificar que NUNCA lanzan error
      expect(() => wrapper.vm.formatUbicacionPrincipal(rowAllNulls)).not.toThrow();
      expect(() => wrapper.vm.formatUbicacionSecundaria(rowAllNulls)).not.toThrow();
      expect(() => wrapper.vm.formatUbicacionPrincipal(null)).not.toThrow();
      expect(() => wrapper.vm.formatUbicacionSecundaria(null)).not.toThrow();
      expect(() => wrapper.vm.formatUbicacionPrincipal(undefined)).not.toThrow();
      expect(() => wrapper.vm.formatUbicacionSecundaria(undefined)).not.toThrow();

      expect(wrapper.vm.formatUbicacionPrincipal(null)).toBe('—');
      expect(wrapper.vm.formatUbicacionSecundaria(null)).toBe('');
      expect(wrapper.vm.formatUbicacionPrincipal(rowAllNulls)).toBe('Espacio individual');
      expect(wrapper.vm.formatUbicacionSecundaria(rowAllNulls)).toBe('');
    });

    it('maneja objeto usuario ausente, undefined o con nombre_completo=null sin errores', async () => {
      const pinia = setupTestEnvironment('responsable');
      const rows = [
        { id: 201, ambito: 'sede', local: { nombre: 'Sede A' }, usuario: null },
        { id: 202, ambito: 'sede', local: { nombre: 'Sede B' }, usuario: undefined },
        { id: 203, ambito: 'sede', local: { nombre: 'Sede C' }, usuario: { id: 30, nombre_completo: null, correo: null } },
        { id: 204, ambito: 'sede', local: { nombre: 'Sede D' }, usuario: { id: 31, nombre_completo: '   ', correo: '' } },
      ];

      espaciosUsuariosService.listar.mockResolvedValueOnce({
        count: rows.length,
        results: rows,
      });

      const wrapper = mountView(pinia);
      await flushPromises();

      const text = wrapper.text();
      expect(text).toContain('Usuario sin nombre');
      expect(text).toContain('—');

      // Probar helper de iniciales directamente
      expect(wrapper.vm.getInitials(null)).toBe('U');
      expect(wrapper.vm.getInitials(undefined)).toBe('U');
      expect(wrapper.vm.getInitials('')).toBe('U');
      // Nota adversarial: strings con solo espacios en blanco '   ' retornan '' en vez de 'U' al evaluar truthy antes del filter(Boolean)
      expect(wrapper.vm.getInitials('   ')).toBe('');
      expect(wrapper.vm.getInitials('Ana')).toBe('A');
      expect(wrapper.vm.getInitials('Ana Maria Perez')).toBe('AM');
    });

    it('evalúa permutaciones de atributos jerárquicos en formatUbicacionSecundaria', async () => {
      const pinia = setupTestEnvironment('admin');
      espaciosUsuariosService.listar.mockResolvedValueOnce({ count: 0, results: [] });
      const wrapper = mountView(pinia);
      await flushPromises();

      // Sede con ciudad
      expect(wrapper.vm.formatUbicacionSecundaria({
        ambito: 'sede',
        local: { nombre: 'Central', ciudad: 'Trujillo' },
      })).toBe('Ciudad: Trujillo');

      // Sede sin ciudad pero con código
      expect(wrapper.vm.formatUbicacionSecundaria({
        ambito: 'sede',
        local: { nombre: 'Central', codigo: 'TRUJ-01' },
      })).toBe('Código: TRUJ-01');

      // Edificio con nombre de sede
      expect(wrapper.vm.formatUbicacionSecundaria({
        ambito: 'edificio',
        local: { nombre: 'Sede Huánuco' },
        edificio: { nombre: 'Pabellón 1' },
      })).toBe('Sede: Sede Huánuco');

      // Edificio sin local pero con código de edificio
      expect(wrapper.vm.formatUbicacionSecundaria({
        ambito: 'edificio',
        local: null,
        edificio: { nombre: 'Pabellón 1', codigo: 'ED-01' },
      })).toBe('Código: ED-01');

      // Piso con nombre de sede
      expect(wrapper.vm.formatUbicacionSecundaria({
        ambito: 'piso',
        local: { nombre: 'Sede Huánuco' },
      })).toBe('Sede: Sede Huánuco');

      // Espacio con subtipo y nombre de sede
      expect(wrapper.vm.formatUbicacionSecundaria({
        ambito: 'espacio',
        local: { nombre: 'Sede Huánuco' },
        espacio: { tipo_display: 'Laboratorio de Cómputo' },
      })).toBe('Laboratorio de Cómputo · Sede Huánuco');

      // Espacio sin local ni subtipo
      expect(wrapper.vm.formatUbicacionSecundaria({
        ambito: 'espacio',
        local: null,
        espacio: null,
      })).toBe('');
    });
  });

  describe('2. Apertura y resiliencia de modales ante datos patológicos', () => {
    it('permite abrir modal de edición sobre fila con valores nulos sin romper el formulario', async () => {
      const pinia = setupTestEnvironment('responsable');
      const malformedRow = {
        id: 888,
        ambito: null,
        local_id: null,
        edificio_id: null,
        piso: null,
        espacio_id: null,
        usuario_id: null,
        tipo_responsabilidad: null,
        activo: false,
      };

      espaciosUsuariosService.listar.mockResolvedValueOnce({
        count: 1,
        results: [malformedRow],
      });

      const wrapper = mountView(pinia);
      await flushPromises();

      // Disparar openEdit
      expect(() => wrapper.vm.openEdit(malformedRow)).not.toThrow();
      await flushPromises();

      expect(wrapper.vm.modalOpen).toBe(true);
      expect(wrapper.vm.isEditing).toBe(true);
      expect(wrapper.vm.form.local_id).toBe('');
      expect(wrapper.vm.form.edificio_id).toBe('');
      expect(wrapper.vm.form.piso).toBe('');
    });

    it('permite abrir y confirmar modal de eliminación sobre fila con usuario nulo', async () => {
      const pinia = setupTestEnvironment('responsable');
      const malformedRow = {
        id: 777,
        ambito: 'sede',
        local: null,
        usuario: null,
      };

      espaciosUsuariosService.listar.mockResolvedValueOnce({
        count: 1,
        results: [malformedRow],
      });

      const wrapper = mountView(pinia);
      await flushPromises();

      // Abrir modal de eliminación
      expect(() => wrapper.vm.askDelete(malformedRow)).not.toThrow();
      await flushPromises();

      expect(wrapper.vm.deleteModalOpen).toBe(true);
      expect(wrapper.vm.pendingDelete).toStrictEqual(malformedRow);

      // El texto dentro del modal de eliminación maneja usuario nulo y ubicación nula sin crash
      expect(wrapper.text()).toContain('Se retirará la asignación de');

      // Cancelar cierre
      wrapper.vm.cancelDelete();
      expect(wrapper.vm.deleteModalOpen).toBe(false);
      expect(wrapper.vm.pendingDelete).toBeNull();
    });
  });

  describe('3. Manejo de Errores de API (HTTP 403 Forbidden y HTTP 400 Bad Request)', () => {
    it('captura HTTP 403 Forbidden al crear asignación en sede no autorizada: muestra toast y no cuelga saving', async () => {
      const pinia = setupTestEnvironment('responsable');
      espaciosUsuariosService.listar.mockResolvedValueOnce({ count: 0, results: [] });

      const wrapper = mountView(pinia);
      await flushPromises();

      // Abrir modal de creación y seleccionar ámbito sede
      wrapper.vm.openCreate();
      wrapper.vm.onAmbitoChange('sede');
      wrapper.vm.form.usuario_id = 5;
      wrapper.vm.form.local_id = 99; // Sede foránea

      // Simular respuesta HTTP 403 del backend
      const error403 = {
        response: {
          status: 403,
          data: {
            detail: 'No tiene permisos para gestionar asignaciones territoriales en sedes ajenas a su administración.',
          },
        },
      };
      espaciosUsuariosService.crear.mockRejectedValueOnce(error403);

      expect(wrapper.vm.saving).toBe(false);

      // Ejecutar submit
      const result = await wrapper.vm.submit();
      await flushPromises();

      // 1. El submit falló limpiamente
      expect(result).toBe(false);

      // 2. El estado saving (guardando) NO se queda congelado en true
      expect(wrapper.vm.saving).toBe(false);

      // 3. El modal permanece abierto para que el usuario pueda corregir su selección
      expect(wrapper.vm.modalOpen).toBe(true);

      // 4. El Toast se activa con el mensaje exacto del backend y tipo 'error'
      expect(wrapper.vm.toast.show).toBe(true);
      expect(wrapper.vm.toast.type).toBe('error');
      expect(wrapper.vm.toast.message).toBe(
        'No tiene permisos para gestionar asignaciones territoriales en sedes ajenas a su administración.'
      );
    });

    it('captura HTTP 400 Bad Request ante asignación territorial duplicada activa: muestra toast y resetea saving', async () => {
      const pinia = setupTestEnvironment('responsable');
      espaciosUsuariosService.listar.mockResolvedValueOnce({ count: 0, results: [] });

      const wrapper = mountView(pinia);
      await flushPromises();

      wrapper.vm.openCreate();
      wrapper.vm.onAmbitoChange('piso');
      wrapper.vm.form.usuario_id = 5;
      wrapper.vm.form.local_id = 1;
      wrapper.vm.form.edificio_id = 10;
      wrapper.vm.form.piso = '1';

      // Simular error HTTP 400 con formato non_field_errors de DRF
      const error400 = {
        response: {
          status: 400,
          data: {
            non_field_errors: ['Ya existe una asignación territorial activa para este usuario en el ámbito seleccionado.'],
          },
        },
      };
      espaciosUsuariosService.crear.mockRejectedValueOnce(error400);

      const result = await wrapper.vm.submit();
      await flushPromises();

      expect(result).toBe(false);
      expect(wrapper.vm.saving).toBe(false);
      expect(wrapper.vm.modalOpen).toBe(true);
      expect(wrapper.vm.toast.show).toBe(true);
      expect(wrapper.vm.toast.type).toBe('error');
      expect(wrapper.vm.toast.message).toBe(
        'Ya existe una asignación territorial activa para este usuario en el ámbito seleccionado.'
      );
    });

    it('captura HTTP 400 con formato de errores por campo ({ errores: { local_id: [...] } })', async () => {
      const pinia = setupTestEnvironment('admin');
      espaciosUsuariosService.listar.mockResolvedValueOnce({ count: 0, results: [] });

      const wrapper = mountView(pinia);
      await flushPromises();

      wrapper.vm.openCreate();
      wrapper.vm.onAmbitoChange('sede');
      wrapper.vm.form.usuario_id = 5;
      wrapper.vm.form.local_id = 1;

      const errorValidation = {
        response: {
          status: 400,
          data: {
            errores: {
              local_id: ['La sede especificada se encuentra en estado inactivo.'],
            },
          },
        },
      };
      espaciosUsuariosService.crear.mockRejectedValueOnce(errorValidation);

      await wrapper.vm.submit();
      await flushPromises();

      expect(wrapper.vm.saving).toBe(false);
      expect(wrapper.vm.toast.show).toBe(true);
      expect(wrapper.vm.toast.type).toBe('error');
      expect(wrapper.vm.toast.message).toBe('La sede especificada se encuentra en estado inactivo.');
    });

    it('captura HTTP 403 en eliminación: no congela saving y reporta error', async () => {
      const pinia = setupTestEnvironment('responsable');
      const itemToDelete = { id: 55, ambito: 'sede', local: { nombre: 'Sede Ajena' } };
      espaciosUsuariosService.listar.mockResolvedValueOnce({ count: 1, results: [itemToDelete] });

      const wrapper = mountView(pinia);
      await flushPromises();

      wrapper.vm.askDelete(itemToDelete);
      expect(wrapper.vm.deleteModalOpen).toBe(true);

      const errorDelete403 = {
        response: {
          status: 403,
          data: {
            error: 'No está autorizado para desasignar personal en esta sede física.',
          },
        },
      };
      espaciosUsuariosService.eliminar.mockRejectedValueOnce(errorDelete403);

      await wrapper.vm.confirmDelete();
      await flushPromises();

      expect(wrapper.vm.saving).toBe(false);
      expect(wrapper.vm.toast.show).toBe(true);
      expect(wrapper.vm.toast.type).toBe('error');
      expect(wrapper.vm.toast.message).toBe('No está autorizado para desasignar personal en esta sede física.');
    });

    it('captura fallo de red o HTTP 500 al listar: no congela loading y emite toast de advertencia', async () => {
      const pinia = setupTestEnvironment('responsable');
      espaciosUsuariosService.listar.mockRejectedValueOnce(new Error('Network Error'));

      const wrapper = mountView(pinia);
      await flushPromises();

      expect(wrapper.vm.loading).toBe(false);
      expect(wrapper.vm.toast.show).toBe(true);
      expect(wrapper.vm.toast.type).toBe('error');
      expect(wrapper.vm.toast.message).toBe('No se pudieron cargar las asignaciones.');
    });

    it('captura HTTP 403 Forbidden al actualizar una asignación existente', async () => {
      const pinia = setupTestEnvironment('responsable');
      const existing = {
        id: 45,
        ambito: 'edificio',
        local_id: 1,
        edificio_id: 10,
        usuario_id: 5,
        tipo_responsabilidad: 'tecnico',
        activo: true,
      };
      espaciosUsuariosService.listar.mockResolvedValueOnce({ count: 1, results: [existing] });

      const wrapper = mountView(pinia);
      await flushPromises();

      wrapper.vm.openEdit(existing);
      expect(wrapper.vm.isEditing).toBe(true);

      const errorUpdate403 = {
        response: {
          status: 403,
          data: {
            detail: 'No tiene permiso para modificar asignaciones en esta sede.',
          },
        },
      };
      espaciosUsuariosService.actualizar.mockRejectedValueOnce(errorUpdate403);

      const result = await wrapper.vm.submit();
      await flushPromises();

      expect(result).toBe(false);
      expect(wrapper.vm.saving).toBe(false);
      expect(wrapper.vm.modalOpen).toBe(true);
      expect(wrapper.vm.toast.show).toBe(true);
      expect(wrapper.vm.toast.type).toBe('error');
      expect(wrapper.vm.toast.message).toBe('No tiene permiso para modificar asignaciones en esta sede.');
    });
  });

  describe('4. Cobertura exhaustiva de badges, iconos y resoluciones límite', () => {
    it('evalúa variantes de formatUbicacionPrincipal ante combinaciones límite', async () => {
      const pinia = setupTestEnvironment('admin');
      espaciosUsuariosService.listar.mockResolvedValueOnce({ count: 0, results: [] });
      const wrapper = mountView(pinia);
      await flushPromises();

      // Prioridad 1: ubicacion_display
      expect(wrapper.vm.formatUbicacionPrincipal({
        ubicacion_display: 'Display Forzado',
        nombre_ambito: 'Nombre Ambito',
      })).toBe('Display Forzado');

      // Prioridad 2: nombre_ambito
      expect(wrapper.vm.formatUbicacionPrincipal({
        nombre_ambito: 'Ambito Forzado',
      })).toBe('Ambito Forzado');

      // Sede con local nulo
      expect(wrapper.vm.formatUbicacionPrincipal({
        ambito: 'sede',
        local: null,
      })).toBe('Sede institucional');

      // Edificio con edificio nulo
      expect(wrapper.vm.formatUbicacionPrincipal({
        ambito: 'edificio',
        edificio: null,
      })).toBe('Pabellón / Edificio');

      // Piso con edificio presente
      expect(wrapper.vm.formatUbicacionPrincipal({
        ambito: 'piso',
        edificio: { nombre: 'Pabellón C' },
        piso: '3',
      })).toBe('Pabellón C · Piso 3');

      // Piso con piso vacío
      expect(wrapper.vm.formatUbicacionPrincipal({
        ambito: 'piso',
        edificio: { nombre: 'Pabellón C' },
        piso: '',
      })).toBe('Pabellón C');

      // Espacio con edificio explícito
      expect(wrapper.vm.formatUbicacionPrincipal({
        ambito: 'espacio',
        espacio: { codigo_espacio: 'A-101' },
        edificio: { nombre: 'Pabellón Alfa' },
      })).toBe('A-101 · Pabellón Alfa');

      // Espacio con pabellon en espacio y sin edificio
      expect(wrapper.vm.formatUbicacionPrincipal({
        ambito: 'espacio',
        espacio: { codigo_espacio: 'A-101', pabellon: 'Pabellón Beta' },
      })).toBe('A-101 · Pabellón Beta');

      // Espacio individual solo con código
      expect(wrapper.vm.formatUbicacionPrincipal({
        ambito: 'espacio',
        espacio: { codigo_espacio: 'A-101' },
      })).toBe('A-101');

      // Ámbito desconocido
      expect(wrapper.vm.formatUbicacionPrincipal({
        ambito: 'desconocido_xyz',
      })).toBe('—');
    });

    it('resuelve correctamente clases, etiquetas e iconos de ámbito y responsabilidad', async () => {
      const pinia = setupTestEnvironment('admin');
      espaciosUsuariosService.listar.mockResolvedValueOnce({ count: 0, results: [] });
      const wrapper = mountView(pinia);
      await flushPromises();

      // Ambito badges
      expect(wrapper.vm.getAmbitoBadgeClass('sede')).toContain('indigo');
      expect(wrapper.vm.getAmbitoBadgeClass('edificio')).toContain('blue');
      expect(wrapper.vm.getAmbitoBadgeClass('piso')).toContain('teal');
      expect(wrapper.vm.getAmbitoBadgeClass('espacio')).toContain('purple');
      expect(wrapper.vm.getAmbitoBadgeClass('desconocido')).toContain('slate');

      // Ambito labels
      expect(wrapper.vm.getAmbitoLabel('sede')).toBe('Sede');
      expect(wrapper.vm.getAmbitoLabel('edificio')).toBe('Pabellón');
      expect(wrapper.vm.getAmbitoLabel('piso')).toBe('Piso');
      expect(wrapper.vm.getAmbitoLabel('espacio')).toBe('Espacio');
      expect(wrapper.vm.getAmbitoLabel('otro')).toBe('Ámbito');

      // Responsabilidad badges
      expect(wrapper.vm.getResponsabilidadBadgeClass('responsable')).toContain('blue');
      expect(wrapper.vm.getResponsabilidadBadgeClass('tecnico')).toContain('emerald');
      expect(wrapper.vm.getResponsabilidadBadgeClass('docente')).toContain('amber');
      expect(wrapper.vm.getResponsabilidadBadgeClass('otro')).toContain('violet');

      // Responsabilidad icons
      expect(wrapper.vm.getResponsabilidadIcon('responsable')).toBeDefined();
      expect(wrapper.vm.getResponsabilidadIcon('tecnico')).toBeDefined();
      expect(wrapper.vm.getResponsabilidadIcon('docente')).toBeDefined();
      expect(wrapper.vm.getResponsabilidadIcon(null)).toBeDefined();
    });
  });
});
