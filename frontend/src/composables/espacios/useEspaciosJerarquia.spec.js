import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h, reactive } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  formatFloorTitle,
  getEspacioHealth,
  useEspaciosJerarquia,
} from '@/composables/espacios/useEspaciosJerarquia';
import { useAuthStore } from '@/stores/auth';

const mockLocales = [
  {
    id: 1,
    codigo: 'LOC-CENTRAL',
    nombre: 'Campus Central Huánuco',
    ciudad: 'Huánuco',
    tipo: 'campus',
    descripcion: 'Sede principal',
    activo: true,
  },
  {
    id: 2,
    codigo: 'LOC-TINGO',
    nombre: 'Sede Tingo María',
    ciudad: 'Tingo María',
    tipo: 'sede',
    descripcion: '',
    activo: true,
  },
];

const mockEdificios = [
  {
    id: 10,
    codigo: 'PAB-01',
    nombre: 'Pabellón 1 - Ciencias',
    descripcion: 'Pabellón principal',
    local_id: 1,
    activo: true,
    configuracion_croquis: {
      pisos: {
        '1': { rows: 4, cols: 8, cells: {} },
        '2': { rows: 4, cols: 8, cells: {} },
        '3': { rows: 4, cols: 8, cells: {} },
      },
    },
  },
  {
    id: 20,
    codigo: 'PAB-02',
    nombre: 'Pabellón 2 - Letras',
    descripcion: '',
    local_id: 2,
    activo: true,
  },
];

const mockEspacios = [
  {
    id: 101,
    codigo_espacio: 'LAB-101',
    tipo: 'laboratorio',
    tipo_display: 'Laboratorio',
    edificio_id: 10,
    pabellon: 'Pabellón 1 - Ciencias',
    piso: '1',
    cantidad_equipos: 20,
    resumen_equipos: { en_uso: 18, en_mantenimiento: 2, dañado: 0, de_baja: 0 },
    activo: true,
  },
  {
    id: 102,
    codigo_espacio: 'LAB-201',
    tipo: 'sala_computo',
    tipo_display: 'Sala de cómputo',
    edificio_id: 10,
    pabellon: 'Pabellón 1 - Ciencias',
    piso: '2',
    cantidad_equipos: 25,
    resumen_equipos: { en_uso: 24, en_mantenimiento: 0, dañado: 1, de_baja: 0 },
    activo: true,
  },
  {
    id: 103,
    codigo_espacio: 'AUL-301',
    tipo: 'aula',
    tipo_display: 'Aula',
    edificio_id: 10,
    pabellon: 'Pabellón 1 - Ciencias',
    piso: '3',
    cantidad_equipos: 30,
    resumen_equipos: { en_uso: 30, en_mantenimiento: 0, dañado: 0, de_baja: 0 },
    activo: true,
  },
];

const mockStats = {
  total: 3,
  activos: 3,
  laboratorios: 2,
  equipos: 75,
};

const mockFloorAssignments = [
  {
    id: 501,
    ambito: 'piso',
    edificio_id: 10,
    piso: '2',
    usuario: { id: 7, nombre: 'Carlos', apellido: 'Mendoza', correo: 'carlos@kairos.edu', rol: 'tecnico' },
    tipo_responsabilidad: 'tecnico',
    tipo_responsabilidad_display: 'Soporte técnico',
    activo: true,
  },
];

const createServices = () => ({
  spaceService: {
    listar: vi.fn().mockResolvedValue({ count: 3, results: mockEspacios }),
    obtenerEstadisticas: vi.fn().mockResolvedValue(mockStats),
    crear: vi.fn().mockImplementation((payload) => Promise.resolve({ id: 999, ...payload })),
    actualizar: vi.fn().mockImplementation((id, payload) => Promise.resolve({ id, ...payload })),
    desactivar: vi.fn().mockResolvedValue(undefined),
  },
  buildingService: {
    listar: vi.fn().mockResolvedValue({ count: 2, results: mockEdificios }),
    crear: vi.fn().mockImplementation((payload) => Promise.resolve({ id: 888, ...payload })),
    actualizar: vi.fn().mockImplementation((id, payload) => Promise.resolve({ id, ...payload })),
    desactivar: vi.fn().mockResolvedValue(undefined),
  },
  localService: {
    listar: vi.fn().mockResolvedValue({ count: 2, results: mockLocales }),
    crear: vi.fn().mockImplementation((payload) => Promise.resolve({ id: 777, ...payload })),
    actualizar: vi.fn().mockImplementation((id, payload) => Promise.resolve({ id, ...payload })),
    desactivar: vi.fn().mockResolvedValue(undefined),
  },
  assignService: {
    listar: vi.fn().mockResolvedValue({ count: 1, results: mockFloorAssignments }),
    obtenerOpciones: vi.fn().mockResolvedValue({
      usuarios: [
        { id: 7, nombre: 'Carlos', apellido: 'Mendoza', rol: 'tecnico', correo: 'carlos@kairos.edu' },
        { id: 8, nombre: 'Ana', apellido: 'Rojas', rol: 'admin', correo: 'ana@kairos.edu' },
      ],
    }),
    crear: vi.fn().mockResolvedValue({ id: 502 }),
    actualizar: vi.fn().mockResolvedValue({ id: 501 }),
    eliminar: vi.fn().mockResolvedValue(undefined),
  },
});

const mountComposable = (services, initialQuery = {}, role = 'admin') => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  useAuthStore().user = { id: 1, nombre: 'Super', rol: role };

  const fakeRoute = reactive({ query: { ...initialQuery } });
  const fakeRouter = {
    replace: vi.fn().mockImplementation(({ query }) => {
      fakeRoute.query = { ...query };
      return Promise.resolve();
    }),
    push: vi.fn().mockImplementation(({ query }) => {
      fakeRoute.query = { ...query };
      return Promise.resolve();
    }),
  };

  mount(defineComponent({
    setup() {
      state = useEspaciosJerarquia({
        ...services,
        route: fakeRoute,
        router: fakeRouter,
      });
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });

  return { state, fakeRoute, fakeRouter };
};

describe('useEspaciosJerarquia', () => {
  let services;

  beforeEach(() => {
    services = createServices();
  });

  describe('Cálculo de salud y títulos de piso', () => {
    it('determina la salud del espacio según equipos dañados o en mantenimiento', () => {
      expect(getEspacioHealth({ cantidad_equipos: 10, resumen_equipos: { dañado: 1 } }).status).toBe('incidencia');
      expect(getEspacioHealth({ cantidad_equipos: 10, resumen_equipos: { en_mantenimiento: 1, dañado: 0 } }).status).toBe('mantenimiento');
      expect(getEspacioHealth({ cantidad_equipos: 10, resumen_equipos: { en_mantenimiento: 0, dañado: 0 } }).status).toBe('optimo');
      expect(getEspacioHealth({ cantidad_equipos: 0 }).status).toBe('vacio');
    });

    it('genera títulos semánticos para pisos', () => {
      expect(formatFloorTitle('3', 3, 0)).toBe('Piso 3 · Nivel Superior');
      expect(formatFloorTitle('2', 3, 1)).toBe('Piso 2 · Nivel Intermedio');
      expect(formatFloorTitle('1', 3, 2)).toBe('Piso 1 · Planta Baja');
      expect(formatFloorTitle('1', 1, 0)).toBe('Piso 1 · Planta Única');
    });
  });

  describe('Carga y agregación de datos territoriales', () => {
    it('carga sedes, edificios, espacios e indicadores al montar', async () => {
      const { state } = mountComposable(services);
      await flushPromises();

      expect(services.localService.listar).toHaveBeenCalledOnce();
      expect(services.buildingService.listar).toHaveBeenCalledOnce();
      expect(services.spaceService.listar).toHaveBeenCalledOnce();
      expect(services.spaceService.obtenerEstadisticas).toHaveBeenCalledOnce();

      expect(state.sedesList.value).toHaveLength(2);
      expect(state.stats.equipos).toBe(75);
    });

    it('agrega métricas de pabellones, ambientes y equipos en sedesList', async () => {
      const { state } = mountComposable(services);
      await flushPromises();

      const central = state.sedesList.value.find((s) => s.id === 1);
      expect(central).toBeDefined();
      expect(central.edificiosCount).toBe(1);
      expect(central.ambientesCount).toBe(3);
      expect(central.equiposCount).toBe(75);
      expect(central.telemetria.operativos).toBe(72);
      expect(central.telemetria.mantenimiento).toBe(2);
      expect(central.telemetria.incidencias).toBe(1);
      expect(central.salud).toBe('incidencia');
    });
  });

  describe('Navegación jerárquica y sincronización de query params', () => {
    it('filtra Lista por ubicación y permite volver al inventario completo', async () => {
      const { state, fakeRoute } = mountComposable(services, { vista: 'inventario', ciudad: 'Tingo María', sede: '2', edificio: '20' });
      await flushPromises();
      expect(state.inventoryFilteredEspacios.value).toHaveLength(0);
      state.clearInventoryScope();
      await flushPromises();
      expect(fakeRoute.query.ciudad).toBeUndefined();
      expect(fakeRoute.query.sede).toBeUndefined();
      expect(state.inventoryFilteredEspacios.value).toHaveLength(3);
      expect(state.currentView.value).toBe('inventario');
    });
    it('inicia en vista jerárquica por defecto y permite cambiar a inventario', async () => {
      const { state, fakeRouter } = mountComposable(services);
      await flushPromises();

      expect(state.currentView.value).toBe('jerarquia');
      state.setVista('inventario');
      expect(state.currentView.value).toBe('inventario');
      expect(fakeRouter.push).toHaveBeenCalledWith({ query: { vista: 'inventario' } });
    });

    it('inicia en inventario si la URL contiene vista=inventario', async () => {
      const { state } = mountComposable(services, { vista: 'inventario' });
      await flushPromises();

      expect(state.currentView.value).toBe('inventario');
    });

    it('ejecuta drill-down seleccionando sede y edificio', async () => {
      const { state, fakeRouter } = mountComposable(services);
      await flushPromises();

      // Nivel 1 -> Seleccionar Sede 1
      state.selectSede(1);
      expect(state.selectedSedeId.value).toBe(1);
      expect(state.selectedSede.value?.nombre).toBe('Campus Central Huánuco');
      expect(state.edificiosDeSede.value).toHaveLength(1);
      expect(fakeRouter.push).toHaveBeenCalledWith({ query: { ciudad: 'Huánuco', sede: 1 } });

      // Nivel 2 -> Seleccionar Edificio 10
      state.selectEdificio(10);
      expect(state.selectedEdificioId.value).toBe(10);
      expect(state.selectedEdificio.value?.nombre).toBe('Pabellón 1 - Ciencias');
      expect(fakeRouter.push).toHaveBeenCalledWith({ query: { ciudad: 'Huánuco', sede: 1, edificio: 10 } });

      // Verificar que los pisos se ordenen verticalmente de arriba a abajo (3, 2, 1)
      await flushPromises();
      const floorKeys = state.pisosDeEdificio.value.map((f) => f.piso);
      expect(floorKeys).toEqual(['3', '2', '1']);

      // Nivel 3 -> Verificar telemetría y técnico del piso 2
      const piso2 = state.pisosDeEdificio.value.find((f) => f.piso === '2');
      expect(piso2.encargado?.usuario_nombre).toBe('Carlos Mendoza');
      expect(piso2.telemetria.operativos).toBe(24);
      expect(piso2.telemetria.incidencias).toBe(1);

      // Regresar a pabellones
      state.resetToEdificios();
      expect(state.selectedEdificioId.value).toBeNull();
      expect(state.selectedSedeId.value).toBe(1);

      // Regresar a sedes
      state.resetToSedes();
      expect(state.selectedSedeId.value).toBeNull();
    });
  });

  describe('Creación contextual de entidades', () => {
    it('crea una nueva sede y recarga la lista', async () => {
      const { state } = mountComposable(services);
      await flushPromises();

      state.openCreateSede();
      expect(state.sedeModalOpen.value).toBe(true);

      Object.assign(state.sedeForm, {
        codigo: 'LOC-AMBO',
        nombre: 'Sede Ambo',
        ciudad: 'Ambo',
        tipo: 'sede',
      });

      const success = await state.submitSede();
      expect(success).toBe(true);
      expect(services.localService.crear).toHaveBeenCalledWith(expect.objectContaining({
        codigo: 'LOC-AMBO',
        nombre: 'Sede Ambo',
        ciudad: 'Ambo',
      }));
      expect(state.sedeModalOpen.value).toBe(false);
      expect(state.toast.type).toBe('success');
    });

    it('crea un nuevo pabellón con sede preseleccionada', async () => {
      const { state } = mountComposable(services);
      await flushPromises();

      state.openCreateEdificio(1);
      expect(state.edificioModalOpen.value).toBe(true);
      expect(state.edificioForm.local_id).toBe(1);

      Object.assign(state.edificioForm, {
        codigo: 'PAB-03',
        nombre: 'Pabellón 3 - Posgrado',
      });

      const success = await state.submitEdificio();
      expect(success).toBe(true);
      expect(services.buildingService.crear).toHaveBeenCalledWith(expect.objectContaining({
        codigo: 'PAB-03',
        nombre: 'Pabellón 3 - Posgrado',
        local_id: 1,
      }));
      expect(state.edificioModalOpen.value).toBe(false);
    });

    it('crea un ambiente asistido con sugerencias de piso existentes', async () => {
      const { state } = mountComposable(services);
      await flushPromises();

      // Abrir creación desde un piso específico (ej. piso 2 de edificio 10)
      state.openCreateEspacio({ sedeId: 1, edificioId: 10, piso: '2' });
      expect(state.espacioModalOpen.value).toBe(true);
      expect(state.espacioForm.local_id).toBe(1);
      expect(state.espacioForm.edificio_id).toBe(10);
      expect(state.espacioForm.piso).toBe('2');

      // Verificar que pisos existentes en el edificio 10 se calculen para los chips
      expect(state.pisosExistentesEnEdificio.value).toContain('1');
      expect(state.pisosExistentesEnEdificio.value).toContain('2');
      expect(state.pisosExistentesEnEdificio.value).toContain('3');

      state.espacioForm.codigo_espacio = 'LAB-202';
      state.espacioForm.tipo = 'laboratorio';

      const success = await state.submitEspacio();
      expect(success).toBe(true);
      expect(services.spaceService.crear).toHaveBeenCalledWith(expect.objectContaining({
        codigo_espacio: 'LAB-202',
        edificio_id: 10,
        piso: '2',
      }));
      expect(state.espacioModalOpen.value).toBe(false);
    });

    it('asigna un técnico responsable a un piso de pabellón', async () => {
      const { state } = mountComposable(services);
      await flushPromises();

      const target = {
        piso: '1',
        edificio_id: 10,
        edificio_nombre: 'Pabellón 1 - Ciencias',
        local_id: 1,
        encargado: null,
      };

      await state.openAssignTechnicianModal(target);
      expect(state.technicianModalOpen.value).toBe(true);
      expect(services.assignService.obtenerOpciones).toHaveBeenCalled();
      expect(state.technicianOptions.value).toHaveLength(2);

      state.technicianForm.usuario_id = 7;
      state.technicianForm.tipo_responsabilidad = 'tecnico';

      await state.submitTechnicianAssignment();
      expect(services.assignService.crear).toHaveBeenCalledWith(expect.objectContaining({
        usuario_id: 7,
        tipo_responsabilidad: 'tecnico',
        ambito: 'piso',
        edificio_id: 10,
        piso: '1',
      }));
      expect(state.technicianModalOpen.value).toBe(false);
    });
  });

  describe('Modal de Croquis 2D', () => {
    it('abre y cierra el croquis 2D para un piso seleccionado', async () => {
      const { state } = mountComposable(services);
      await flushPromises();

      const floor = { key: '2', piso: '2', label: 'Piso 2 · Nivel Intermedio' };
      state.openCroquisModal(floor);
      expect(state.croquisModalOpen.value).toBe(true);
      expect(state.croquisTargetFloor.value).toEqual(floor);

      state.closeCroquisModal();
      expect(state.croquisModalOpen.value).toBe(false);
      expect(state.croquisTargetFloor.value).toBeNull();
    });
  });
});
