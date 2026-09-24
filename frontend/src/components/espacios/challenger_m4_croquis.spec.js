import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h, ref } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import CroquisPiso from '@/components/espacios/CroquisPiso.vue';
import { useCampusTecnologico } from '@/composables/espacios/useCampusTecnologico';
import { useAuthStore } from '@/stores/auth';

const createMockFloor = (overrides = {}) => ({
  key: '2',
  piso: '2',
  label: 'Piso 2',
  edificio_id: 10,
  edificio_nombre: 'Pabellón Central',
  local_id: 1,
  labs: 2,
  aulas: 1,
  spaces: [],
  allSpaces: [
    {
      id: 101,
      codigo_espacio: 'LAB-201',
      tipo: 'laboratorio',
      tipo_display: 'Laboratorio',
      cantidad_equipos: 15,
      resumen_equipos: { dañado: 1, en_mantenimiento: 1 },
      encargados_directos: [
        { id: 1, usuario_nombre: 'Ing. Elena Directa', tipo_responsabilidad_display: 'Docente responsable' },
      ],
      encargados_heredados: [
        { id: 2, usuario_nombre: 'Carlos Heredado', origen: 'Pabellón Central · Piso 2' },
      ],
    },
    {
      id: 102,
      codigo_espacio: 'LAB-202',
      tipo: 'sala_computo',
      tipo_display: 'Sala de cómputo',
      cantidad_equipos: 10,
      resumen_equipos: { dañado: 0, en_mantenimiento: 0 },
      encargados_directos: [],
      encargados_heredados: [
        { id: 3, usuario_nombre: 'Carlos Heredado', origen: 'Pabellón Central · Piso 2' },
      ],
    },
    {
      id: 103,
      codigo_espacio: 'AULA-203',
      tipo: 'aula',
      tipo_display: 'Aula de teoría',
      cantidad_equipos: 0,
      resumen_equipos: {},
      encargados_directos: [
        { id: 4, usuario_nombre: 'Prof. Ana María', tipo_responsabilidad_display: 'Docente titular' },
        { id: 5, usuario_nombre: 'Prof. Roberto Auxiliar', tipo_responsabilidad_display: 'Docente adjunto' },
        { id: 6, usuario_nombre: 'Ing. Supervisor Extra', tipo_responsabilidad_display: 'Soporte técnico' },
      ],
      encargados_heredados: [],
    },
  ],
  layout: {
    filas: 3,
    columnas: 8,
    ambientes: [
      { espacio_id: 101, fila: 1, columna: 1, ancho: 2, alto: 2 },
      { espacio_id: 102, fila: 1, columna: 3, ancho: 2, alto: 2 },
      { espacio_id: 103, fila: 1, columna: 5, ancho: 2, alto: 2 },
    ],
    pasillos: [{ fila: 2, columna: 1 }, { fila: 2, columna: 2 }],
  },
  encargado: null,
  ...overrides,
});

describe('Adversarial Stress Test: CroquisPiso & In-Situ Assignment (Milestone 4)', () => {
  beforeEach(() => {
    const pinia = createPinia();
    setActivePinia(pinia);
  });

  describe('1. Floor Technician State & Iconography (Sin encargado vs Con encargado)', () => {
    it('renderiza correctamente el estado sin encargado con badge vacio e icono Wrench', () => {
      const floorSinEncargado = createMockFloor({ encargado: null });
      const wrapper = mount(CroquisPiso, {
        props: { floor: floorSinEncargado, canEdit: false },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      const emptyBadge = wrapper.find('[data-testid="floor-technician-empty"]');
      expect(emptyBadge.exists()).toBe(true);
      expect(emptyBadge.text()).toContain('Sin encargado asignado');

      const wrenchIcon = emptyBadge.find('svg.lucide-wrench');
      expect(wrenchIcon.exists()).toBe(true);

      expect(wrapper.find('[data-testid="floor-technician-badge"]').exists()).toBe(false);
      expect(wrapper.find('svg.lucide-user-round-check').exists()).toBe(false);
    });

    it('renderiza badge completo con nombre, texto de ambito e icono UserRoundCheck cuando tiene tecnico', () => {
      const floorConEncargado = createMockFloor({
        encargado: {
          id: 77,
          usuario_id: 12,
          usuario_nombre: 'Marcos Técnico Especialista',
          badge_texto: 'Encargado Piso 2 · Pabellón Central',
          tipo_responsabilidad: 'tecnico',
          activo: true,
        },
      });

      const wrapper = mount(CroquisPiso, {
        props: { floor: floorConEncargado, canEdit: false },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      const techBadge = wrapper.find('[data-testid="floor-technician-badge"]');
      expect(techBadge.exists()).toBe(true);
      expect(techBadge.text()).toContain('Marcos Técnico Especialista');
      expect(techBadge.text()).toContain('Encargado Piso 2 · Pabellón Central');

      const userRoundCheckIcon = techBadge.find('svg.lucide-user-round-check');
      expect(userRoundCheckIcon.exists()).toBe(true);

      expect(wrapper.find('[data-testid="floor-technician-empty"]').exists()).toBe(false);
      expect(wrapper.find('svg.lucide-wrench').exists()).toBe(false);
    });

    it('aplica texto por defecto "Encargado del piso" si badge_texto es nulo o ausente', () => {
      const floorFallbackBadge = createMockFloor({
        encargado: {
          id: 88,
          usuario_id: 15,
          usuario_nombre: 'Rosa Técnica',
          badge_texto: null,
        },
      });

      const wrapper = mount(CroquisPiso, {
        props: { floor: floorFallbackBadge, canEdit: false },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      const techBadge = wrapper.find('[data-testid="floor-technician-badge"]');
      expect(techBadge.text()).toContain('Encargado del piso');
      expect(techBadge.text()).toContain('Rosa Técnica');
    });

    it('extrae usuario.nombre_completo de objeto anidado si usuario_nombre no esta a primer nivel', () => {
      const floorNestedUser = createMockFloor({
        encargado: {
          id: 89,
          usuario: { nombre_completo: 'Ing. Gabriel Anidado' },
          badge_texto: 'Referente de Piso',
        },
      });

      const wrapper = mount(CroquisPiso, {
        props: { floor: floorNestedUser, canEdit: false },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      const techBadge = wrapper.find('[data-testid="floor-technician-badge"]');
      expect(techBadge.text()).toContain('Ing. Gabriel Anidado');
    });

    it('resiste encargado con objeto vacio {} mostrando textos de contingencia sin arrojar excepcion', () => {
      const floorEmptyEncargado = createMockFloor({ encargado: {} });
      const wrapper = mount(CroquisPiso, {
        props: { floor: floorEmptyEncargado, canEdit: false },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      const techBadge = wrapper.find('[data-testid="floor-technician-badge"]');
      expect(techBadge.exists()).toBe(true);
      expect(techBadge.text()).toContain('Encargado del piso');
      expect(techBadge.text()).toContain('Técnico asignado');
    });
  });

  describe('2. Permission Stress: canEdit: false vs canEdit: true', () => {
    it('canEdit: false omite estrictamente ambos botones Asignar y Cambiar en piso sin encargado', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: createMockFloor({ encargado: null }), canEdit: false },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      expect(wrapper.find('[data-testid="assign-floor-technician"]').exists()).toBe(false);
      expect(wrapper.find('[data-testid="edit-floor-technician"]').exists()).toBe(false);
      expect(wrapper.text()).toContain('Sin encargado asignado');
    });

    it('canEdit: false omite estrictamente ambos botones Asignar y Cambiar en piso con encargado', () => {
      const wrapper = mount(CroquisPiso, {
        props: {
          floor: createMockFloor({
            encargado: { id: 1, usuario_nombre: 'Técnico Permanente' },
          }),
          canEdit: false,
        },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      expect(wrapper.find('[data-testid="assign-floor-technician"]').exists()).toBe(false);
      expect(wrapper.find('[data-testid="edit-floor-technician"]').exists()).toBe(false);
      expect(wrapper.text()).toContain('Técnico Permanente');
    });

    it('canEdit: false omite botones de diseno y de edicion/eliminacion de ambientes', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: createMockFloor(), canEdit: false },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      expect(wrapper.text()).not.toContain('Diseñar piso');
      expect(wrapper.text()).not.toContain('Ambiente');
      expect(wrapper.find('button[aria-label="Editar ambiente"]').exists()).toBe(false);
      expect(wrapper.find('button[aria-label="Desactivar ambiente"]').exists()).toBe(false);
    });

    it('canEdit: true muestra boton Asignar en piso vacio y emite assign-technician con payload enriquecido', async () => {
      const floor = createMockFloor({
        encargado: null,
        edificio_id: 10,
        local_id: 1,
        edificio_nombre: 'Pabellón Central',
        piso: '2',
      });
      const wrapper = mount(CroquisPiso, {
        props: { floor, canEdit: true, editing: false },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      const assignBtn = wrapper.find('[data-testid="assign-floor-technician"]');
      expect(assignBtn.exists()).toBe(true);
      expect(assignBtn.text()).toContain('Asignar');
      expect(assignBtn.find('svg.lucide-plus').exists()).toBe(true);

      await assignBtn.trigger('click');

      expect(wrapper.emitted('assign-technician')).toHaveLength(1);
      const payload = wrapper.emitted('assign-technician')[0][0];
      expect(payload).toEqual(expect.objectContaining({
        piso: '2',
        edificio_id: 10,
        local_id: 1,
        edificio_nombre: 'Pabellón Central',
        encargado: null,
      }));
    });

    it('canEdit: true muestra boton Cambiar en piso asignado y emite assign-technician con encargado actual', async () => {
      const encargadoData = {
        id: 55,
        usuario_id: 8,
        usuario_nombre: 'Laura Técnica',
        tipo_responsabilidad: 'tecnico',
      };
      const floor = createMockFloor({
        encargado: encargadoData,
        edificio_id: 10,
        local_id: 1,
        edificio_nombre: 'Pabellón Central',
        piso: '2',
      });
      const wrapper = mount(CroquisPiso, {
        props: { floor, canEdit: true, editing: false },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      const editBtn = wrapper.find('[data-testid="edit-floor-technician"]');
      expect(editBtn.exists()).toBe(true);
      expect(editBtn.text()).toContain('Cambiar');
      expect(editBtn.find('svg.lucide-pencil').exists()).toBe(true);

      await editBtn.trigger('click');

      expect(wrapper.emitted('assign-technician')).toHaveLength(1);
      const payload = wrapper.emitted('assign-technician')[0][0];
      expect(payload).toEqual(expect.objectContaining({
        piso: '2',
        edificio_id: 10,
        local_id: 1,
        edificio_nombre: 'Pabellón Central',
        encargado: expect.objectContaining({ id: 55, usuario_nombre: 'Laura Técnica' }),
      }));
    });

    it('oculta botones Asignar y Cambiar cuando el plano esta en modo edicion (editing: true)', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: createMockFloor({ encargado: null }), canEdit: true, editing: true },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      expect(wrapper.find('[data-testid="assign-floor-technician"]').exists()).toBe(false);
      expect(wrapper.find('[data-testid="edit-floor-technician"]').exists()).toBe(false);
    });
  });

  describe('3. Space-Level Technician Badges, Fallback & Strict Precedence', () => {
    it('muestra pill de encargado heredado con icono Layers y sufijo (Heredado) cuando no hay directo', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: createMockFloor() },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      // LAB-202 tiene encargado_heredado pero NO encargado_directo
      const inheritedBadges = wrapper.findAll('[data-testid="space-inherited-encargado"]');
      expect(inheritedBadges.length).toBeGreaterThanOrEqual(1);

      const inherited = inheritedBadges.find((b) => b.text().includes('Carlos Heredado'));
      expect(inherited).toBeDefined();
      expect(inherited.text()).toContain('(Heredado)');
      expect(inherited.find('svg.lucide-layers').exists()).toBe(true);
      expect(inherited.attributes('title')).toContain('Pabellón Central · Piso 2');
    });

    it('prioriza estrictamente encargado directo sobre heredado cuando ambos estan presentes en el espacio', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: createMockFloor() },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      // LAB-201 tiene encargado directo (Ing. Elena Directa) Y encargado heredado (Carlos Heredado)
      // Debe renderizar space-direct-encargado y SUPRIMIR space-inherited-encargado en ese article
      const articles = wrapper.findAll('article');
      const lab201 = articles.find((a) => a.text().includes('LAB-201'));
      expect(lab201).toBeDefined();

      const directBadge = lab201.find('[data-testid="space-direct-encargado"]');
      expect(directBadge.exists()).toBe(true);
      expect(directBadge.text()).toContain('Ing. Elena Directa');
      expect(directBadge.find('svg.lucide-user-check').exists()).toBe(true);
      expect(directBadge.attributes('title')).toContain('Docente responsable');

      // Verificacion de precedencia estricta: NO debe existir el pill de heredado en LAB-201
      const inheritedBadgeInLab201 = lab201.find('[data-testid="space-inherited-encargado"]');
      expect(inheritedBadgeInLab201.exists()).toBe(false);
    });

    it('maneja multiples encargados directos mostrando primer nombre, contador +N y tooltip completo', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: createMockFloor() },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      // AULA-203 tiene 3 encargados directos
      const articles = wrapper.findAll('article');
      const aula203 = articles.find((a) => a.text().includes('AULA-203'));
      expect(aula203).toBeDefined();

      const directBadge = aula203.find('[data-testid="space-direct-encargado"]');
      expect(directBadge.exists()).toBe(true);
      expect(directBadge.text()).toContain('Prof. Ana María');
      expect(directBadge.text()).toContain('+2'); // 3 encargados - 1 = +2

      const tooltip = directBadge.attributes('title');
      expect(tooltip).toContain('Prof. Ana María');
      expect(tooltip).toContain('Prof. Roberto Auxiliar');
      expect(tooltip).toContain('Ing. Supervisor Extra');
    });

    it('renderiza badges de ambientes tanto en modo visualizacion como en modo edicion', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: createMockFloor(), editing: true },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      const directBadges = wrapper.findAll('[data-testid="space-direct-encargado"]');
      const inheritedBadges = wrapper.findAll('[data-testid="space-inherited-encargado"]');
      expect(directBadges.length).toBeGreaterThan(0);
      expect(inheritedBadges.length).toBeGreaterThan(0);
    });
  });

  describe('4. Pathological & Minimal props.floor Mock (Fault Tolerance & Zero Runtime Exceptions)', () => {
    it('monta con cero excepciones cuando props.floor solo tiene key basico', () => {
      const minimalFloor = { key: '1' };
      let wrapper;
      expect(() => {
        wrapper = mount(CroquisPiso, {
          props: { floor: minimalFloor },
          global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
        });
      }).not.toThrow();

      expect(wrapper.text()).toContain('Sin encargado asignado');
      expect(wrapper.findAll('article')).toHaveLength(0);
    });

    it('monta con cero excepciones con objeto vacio {}', () => {
      let wrapper;
      expect(() => {
        wrapper = mount(CroquisPiso, {
          props: { floor: {} },
          global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
        });
      }).not.toThrow();

      expect(wrapper.text()).toContain('Sin encargado asignado');
    });

    it('monta con cero excepciones cuando todas las propiedades de floor son explicitamente null', () => {
      const nullFloor = {
        key: null,
        piso: null,
        label: null,
        edificio_id: null,
        local_id: null,
        edificio_nombre: null,
        encargado: null,
        allSpaces: null,
        spaces: null,
        layout: null,
        labs: null,
        aulas: null,
      };

      let wrapper;
      expect(() => {
        wrapper = mount(CroquisPiso, {
          props: { floor: nullFloor },
          global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
        });
      }).not.toThrow();

      expect(wrapper.text()).toContain('Sin encargado asignado');
      expect(wrapper.findAll('article')).toHaveLength(0);
    });

    it('tolera ambientes con arrays de encargados nulos o indefinidos sin lanzar excepciones', () => {
      const floorWithCorruptSpaces = createMockFloor({
        allSpaces: [
          {
            id: 201,
            codigo_espacio: 'CORRUPT-1',
            tipo: 'laboratorio',
            encargados_directos: null,
            encargados_heredados: null,
            resumen_equipos: null,
          },
          {
            id: 202,
            codigo_espacio: 'CORRUPT-2',
            tipo: 'aula',
            encargados_directos: undefined,
            encargados_heredados: undefined,
            resumen_equipos: undefined,
          },
        ],
        layout: {
          filas: 2,
          columnas: 4,
          ambientes: [
            { espacio_id: 201, fila: 1, columna: 1, ancho: 1, alto: 1 },
            { espacio_id: 202, fila: 1, columna: 2, ancho: 1, alto: 1 },
            // Referencia a ambiente inexistente (dangling reference)
            { espacio_id: 9999, fila: 2, columna: 1, ancho: 1, alto: 1 },
          ],
        },
      });

      let wrapper;
      expect(() => {
        wrapper = mount(CroquisPiso, {
          props: { floor: floorWithCorruptSpaces },
          global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
        });
      }).not.toThrow();

      // Solo los 2 ambientes validos deben renderizarse
      const articles = wrapper.findAll('article');
      expect(articles).toHaveLength(2);
      expect(wrapper.find('[data-testid="space-direct-encargado"]').exists()).toBe(false);
      expect(wrapper.find('[data-testid="space-inherited-encargado"]').exists()).toBe(false);
    });

    it('resiste click en celda sin lanzar excepciones en modo edicion con layout minimo', async () => {
      const minimalFloor = {
        key: '1',
        layout: { filas: 2, columnas: 2, ambientes: [], pasillos: [] },
      };

      const wrapper = mount(CroquisPiso, {
        props: { floor: minimalFloor, editing: true },
        global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
      });

      const cellButtons = wrapper.findAll('button[aria-label^="Celda"]');
      expect(cellButtons.length).toBe(4);
      await cellButtons[0].trigger('click');
      expect(wrapper.emitted('cell-click')).toHaveLength(1);
    });
  });

  describe('5. In-Situ Modal Workflow & Composable Integration (useCampusTecnologico)', () => {
    const createTestServices = () => ({
      spaceService: {
        listar: vi.fn().mockResolvedValue({
          results: [
            { id: 1, codigo_espacio: 'LAB-101', tipo: 'laboratorio', edificio_id: 1, piso: '1', cantidad_equipos: 5, activo: true },
          ],
        }),
        crear: vi.fn().mockResolvedValue({ id: 2 }),
        actualizar: vi.fn().mockResolvedValue({ id: 1 }),
        desactivar: vi.fn().mockResolvedValue(undefined),
      },
      buildingService: {
        listar: vi.fn().mockResolvedValue({
          results: [
            { id: 1, codigo: 'EDIF-01', nombre: 'Edificio Central', local_id: 1, activo: true, configuracion_croquis: {} },
          ],
        }),
        crear: vi.fn(),
        actualizar: vi.fn(),
        desactivar: vi.fn(),
        guardarCroquisPiso: vi.fn(),
      },
      localService: {
        listar: vi.fn().mockResolvedValue({
          results: [{ id: 1, codigo: 'LOC-01', nombre: 'Campus Principal', activo: true }],
        }),
      },
      asignacionesService: {
        listar: vi.fn().mockResolvedValue({
          results: [
            {
              id: 99,
              usuario_id: 10,
              usuario: { id: 10, nombre: 'Tomás', apellido: 'Técnico', nombre_completo: 'Tomás Técnico', correo: 'tomas@test.com' },
              tipo_responsabilidad: 'tecnico',
              tipo_responsabilidad_display: 'Técnico encargado',
              ambito: 'piso',
              piso: '1',
              edificio_id: 1,
              local_id: 1,
              activo: true,
              badge_texto: 'Encargado Piso 1 · Edificio Central',
            },
          ],
        }),
        crear: vi.fn().mockResolvedValue({ id: 100 }),
        actualizar: vi.fn().mockResolvedValue({ id: 99 }),
        obtenerOpciones: vi.fn().mockResolvedValue({
          usuarios: [
            { id: 10, nombre: 'Tomás', apellido: 'Técnico', rol: 'tecnico', correo: 'tomas@test.com' },
            { id: 20, nombre: 'Elena', apellido: 'Responsable', rol: 'responsable', correo: 'elena@test.com' },
            { id: 30, nombre: 'Carlos', apellido: 'Docente', rol: 'docente', correo: 'carlos@test.com' },
          ],
        }),
      },
    });

    const mountComposableWithRole = async (services, role = 'admin') => {
      let state;
      const pinia = createPinia();
      setActivePinia(pinia);
      useAuthStore().user = { id: 1, rol: role };

      mount(defineComponent({
        setup() {
          state = useCampusTecnologico(
            services.spaceService,
            services.buildingService,
            services.localService,
            {},
            services.asignacionesService,
          );
          return () => h('div');
        },
      }), { global: { plugins: [pinia] } });

      await flushPromises();
      return state;
    };

    it('abre modal para piso con tecnico pre-rellenando datos existentes', async () => {
      const services = createTestServices();
      const state = await mountComposableWithRole(services, 'admin');

      const targetPisoConTecnico = {
        piso: '1',
        edificio_id: 1,
        local_id: 1,
        edificio_nombre: 'Edificio Central',
        encargado: { id: 99, usuario_id: 10, tipo_responsabilidad: 'tecnico' },
      };

      await state.openAssignTechnicianModal(targetPisoConTecnico);

      expect(state.technicianModalOpen.value).toBe(true);
      expect(state.technicianForm.assignment_id).toBe(99);
      expect(state.technicianForm.usuario_id).toBe(10);
      expect(state.technicianForm.tipo_responsabilidad).toBe('tecnico');
      expect(state.technicianTarget.value).toEqual(targetPisoConTecnico);

      // Solo usuarios con rol tecnico, responsable, admin se filtran en technicianOptions
      expect(state.technicianOptions.value).toHaveLength(2); // tomas (tecnico) y elena (responsable); carlos (docente) excluido
      expect(state.technicianOptions.value.map((o) => o.value)).toEqual([10, 20]);
    });

    it('abre modal para piso sin tecnico dejando formulario limpio para nueva asignacion', async () => {
      const services = createTestServices();
      const state = await mountComposableWithRole(services, 'admin');

      const targetPisoSinTecnico = {
        piso: '2',
        edificio_id: 1,
        local_id: 1,
        edificio_nombre: 'Edificio Central',
        encargado: null,
      };

      await state.openAssignTechnicianModal(targetPisoSinTecnico);

      expect(state.technicianModalOpen.value).toBe(true);
      expect(state.technicianForm.assignment_id).toBeNull();
      expect(state.technicianForm.usuario_id).toBe('');
      expect(state.technicianForm.tipo_responsabilidad).toBe('tecnico');
    });

    it('bloquea openAssignTechnicianModal si canEdit es false (ej. rol tecnico)', async () => {
      const services = createTestServices();
      const state = await mountComposableWithRole(services, 'tecnico');

      expect(state.canEdit.value).toBe(false);

      await state.openAssignTechnicianModal({
        piso: '1',
        edificio_id: 1,
        local_id: 1,
      });

      expect(state.technicianModalOpen.value).toBe(false);
      expect(services.asignacionesService.obtenerOpciones).not.toHaveBeenCalled();
    });

    it('crea nueva asignacion territorial de piso con payload estricto al enviar formulario', async () => {
      const services = createTestServices();
      const state = await mountComposableWithRole(services, 'admin');

      await state.openAssignTechnicianModal({
        piso: ' 2 ',
        edificio_id: 1,
        local_id: 1,
        encargado: null,
      });

      state.technicianForm.usuario_id = 20;
      state.technicianForm.tipo_responsabilidad = 'responsable';

      await state.submitTechnicianAssignment();

      expect(services.asignacionesService.crear).toHaveBeenCalledWith({
        usuario_id: 20,
        tipo_responsabilidad: 'responsable',
        activo: true,
        ambito: 'piso',
        local_id: 1,
        edificio_id: 1,
        piso: '2',
        espacio_id: null,
      });
      expect(state.technicianModalOpen.value).toBe(false);
      expect(state.toast.type).toBe('success');
      expect(services.asignacionesService.listar).toHaveBeenCalled();
    });

    it('actualiza asignacion existente via actualizar cuando assignment_id esta presente', async () => {
      const services = createTestServices();
      const state = await mountComposableWithRole(services, 'admin');

      await state.openAssignTechnicianModal({
        piso: '1',
        edificio_id: 1,
        local_id: 1,
        encargado: { id: 99, usuario_id: 10, tipo_responsabilidad: 'tecnico' },
      });

      state.technicianForm.usuario_id = 10;
      state.technicianForm.tipo_responsabilidad = 'tecnico';

      await state.submitTechnicianAssignment();

      expect(services.asignacionesService.actualizar).toHaveBeenCalledWith(99, {
        usuario_id: 10,
        tipo_responsabilidad: 'tecnico',
        activo: true,
        ambito: 'piso',
        local_id: 1,
        edificio_id: 1,
        piso: '1',
        espacio_id: null,
      });
      expect(state.technicianModalOpen.value).toBe(false);
      expect(state.toast.type).toBe('success');
    });

    it('captura errores de API al asignar (ej. 403 Forbidden) mostrando toast de error sin corromper estado', async () => {
      const services = createTestServices();
      services.asignacionesService.crear.mockRejectedValueOnce({
        response: { status: 403, data: { detail: 'No tienes permiso en esta sede territorial.' } },
      });

      const state = await mountComposableWithRole(services, 'admin');

      await state.openAssignTechnicianModal({
        piso: '2',
        edificio_id: 1,
        local_id: 1,
        encargado: null,
      });

      state.technicianForm.usuario_id = 20;
      await state.submitTechnicianAssignment();

      expect(state.toast.type).toBe('error');
      expect(state.toast.message).toContain('No tienes permiso');
      expect(state.technicianSaving.value).toBe(false);
    });

    it('no envia peticion si usuario_id no esta seleccionado o formulario esta vacio', async () => {
      const services = createTestServices();
      const state = await mountComposableWithRole(services, 'admin');

      await state.openAssignTechnicianModal({
        piso: '1',
        edificio_id: 1,
        local_id: 1,
        encargado: null,
      });

      state.technicianForm.usuario_id = '';
      await state.submitTechnicianAssignment();

      expect(services.asignacionesService.crear).not.toHaveBeenCalled();
      expect(services.asignacionesService.actualizar).not.toHaveBeenCalled();
    });
  });
});
