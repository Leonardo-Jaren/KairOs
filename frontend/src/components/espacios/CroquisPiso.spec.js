import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import CroquisPiso from '@/components/espacios/CroquisPiso.vue';

const createFloor = (overrides = {}) => ({
  key: '2',
  piso: '2',
  label: 'Piso 2',
  edificio_id: 2,
  edificio_nombre: 'Pabellón A',
  local_id: 1,
  labs: 2,
  aulas: 0,
  spaces: [],
  allSpaces: [
    {
      id: 1,
      codigo_espacio: 'LAB-201',
      tipo: 'laboratorio',
      tipo_display: 'Laboratorio',
      cantidad_equipos: 12,
      resumen_equipos: { dañado: 1, en_mantenimiento: 2 },
      encargados_directos: [
        { id: 10, usuario_nombre: 'Carlos Directo', tipo_responsabilidad_display: 'Docente' },
      ],
      encargados_heredados: [],
    },
    {
      id: 2,
      codigo_espacio: 'LAB-202',
      tipo: 'sala_computo',
      tipo_display: 'Sala de cómputo',
      cantidad_equipos: 8,
      resumen_equipos: { dañado: 0, en_mantenimiento: 1 },
      encargados_directos: [],
      encargados_heredados: [
        { id: 11, usuario_nombre: 'Tomás Heredado', origen: 'Piso 2 · Pabellón A' },
      ],
    },
  ],
  layout: {
    filas: 3,
    columnas: 8,
    ambientes: [
      { espacio_id: 1, fila: 1, columna: 1, ancho: 2, alto: 2 },
      { espacio_id: 2, fila: 1, columna: 3, ancho: 2, alto: 2 },
    ],
    pasillos: [],
  },
  encargado: null,
  ...overrides,
});

describe('CroquisPiso', () => {
  it('destaca los ambientes según las alertas de sus equipos', () => {
    const wrapper = mount(CroquisPiso, {
      props: { floor: createFloor() },
      global: {
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
        },
      },
    });
    const rooms = wrapper.findAll('article');

    expect(rooms[0].classes()).toContain('border-danger-300');
    expect(rooms[0].text()).toContain('3');
    expect(rooms[1].classes()).toContain('border-warning-300');
    expect(rooms[1].text()).toContain('1');
    expect(wrapper.text()).toContain('Mantenimiento');
    expect(wrapper.text()).toContain('Con falla');
  });

  it('renderiza badge con nombre y rol cuando el piso tiene encargado asignado', () => {
    const floorWithTechnician = createFloor({
      encargado: {
        id: 45,
        usuario_id: 3,
        usuario_nombre: 'Tomás Técnico Vargas',
        tipo_responsabilidad: 'tecnico',
        badge_texto: 'Encargado Piso 2 · Pabellón A',
        activo: true,
      },
    });

    const wrapper = mount(CroquisPiso, {
      props: { floor: floorWithTechnician },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    const badge = wrapper.find('[data-testid="floor-technician-badge"]');
    expect(badge.exists()).toBe(true);
    expect(badge.text()).toContain('Tomás Técnico Vargas');
    expect(badge.text()).toContain('Encargado Piso 2 · Pabellón A');
    expect(wrapper.find('svg.lucide-user-round-check').exists()).toBe(true);
    expect(wrapper.find('[data-testid="floor-technician-empty"]').exists()).toBe(false);
  });

  it('renderiza estado vacío cuando el piso no tiene técnico asignado', () => {
    const wrapper = mount(CroquisPiso, {
      props: { floor: createFloor({ encargado: null }) },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    const empty = wrapper.find('[data-testid="floor-technician-empty"]');
    expect(empty.exists()).toBe(true);
    expect(empty.text()).toContain('Sin encargado asignado');
    expect(wrapper.find('[data-testid="floor-technician-badge"]').exists()).toBe(false);
  });

  it('muestra botones de acción y emite assign-technician al hacer clic cuando canEdit es true', async () => {
    // Caso A: Piso sin encargado -> botón Asignar
    const wrapperSin = mount(CroquisPiso, {
      props: { floor: createFloor({ encargado: null }), canEdit: true, editing: false },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    const assignBtn = wrapperSin.find('[data-testid="assign-floor-technician"]');
    expect(assignBtn.exists()).toBe(true);
    await assignBtn.trigger('click');

    expect(wrapperSin.emitted('assign-technician')).toBeTruthy();
    expect(wrapperSin.emitted('assign-technician')[0][0]).toEqual(
      expect.objectContaining({
        piso: '2',
        edificio_id: 2,
        local_id: 1,
        edificio_nombre: 'Pabellón A',
        encargado: null,
      }),
    );

    // Caso B: Piso con encargado -> botón Cambiar
    const wrapperCon = mount(CroquisPiso, {
      props: {
        floor: createFloor({
          encargado: {
            id: 45,
            usuario_id: 3,
            usuario_nombre: 'Tomás Técnico Vargas',
            tipo_responsabilidad: 'tecnico',
          },
        }),
        canEdit: true,
        editing: false,
      },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    const editBtn = wrapperCon.find('[data-testid="edit-floor-technician"]');
    expect(editBtn.exists()).toBe(true);
    await editBtn.trigger('click');

    expect(wrapperCon.emitted('assign-technician')).toBeTruthy();
    expect(wrapperCon.emitted('assign-technician')[0][0].encargado?.usuario_nombre).toBe('Tomás Técnico Vargas');
  });

  it('restringe estrictamente acciones de modificación cuando canEdit es false (solo lectura)', () => {
    // Piso sin encargado con canEdit: false
    const wrapperSin = mount(CroquisPiso, {
      props: { floor: createFloor({ encargado: null }), canEdit: false },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    expect(wrapperSin.text()).toContain('Sin encargado asignado');
    expect(wrapperSin.find('[data-testid="assign-floor-technician"]').exists()).toBe(false);
    expect(wrapperSin.find('[data-testid="edit-floor-technician"]').exists()).toBe(false);

    // Piso con encargado con canEdit: false
    const wrapperCon = mount(CroquisPiso, {
      props: {
        floor: createFloor({
          encargado: { id: 45, usuario_nombre: 'Carlos Tecnico' },
        }),
        canEdit: false,
      },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    expect(wrapperCon.text()).toContain('Carlos Tecnico');
    expect(wrapperCon.find('[data-testid="assign-floor-technician"]').exists()).toBe(false);
    expect(wrapperCon.find('[data-testid="edit-floor-technician"]').exists()).toBe(false);
  });

  it('renderiza badges de encargados directos y heredados en los ambientes del croquis', () => {
    const wrapper = mount(CroquisPiso, {
      props: { floor: createFloor() },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    const directBadges = wrapper.findAll('[data-testid="space-direct-encargado"]');
    expect(directBadges.length).toBeGreaterThan(0);
    expect(directBadges[0].text()).toContain('Carlos Directo');

    const inheritedBadges = wrapper.findAll('[data-testid="space-inherited-encargado"]');
    expect(inheritedBadges.length).toBeGreaterThan(0);
    expect(inheritedBadges[0].text()).toContain('Tomás Heredado');
    expect(inheritedBadges[0].text()).toContain('(Heredado)');
  });

  it('mantiene tolerancia a fallos cuando props.floor tiene estructura mínima o nula', () => {
    const minimalFloor = { key: '1' };
    const wrapper = mount(CroquisPiso, {
      props: { floor: minimalFloor },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    });

    expect(wrapper.text()).toContain('Sin encargado asignado');
    expect(wrapper.findAll('article')).toHaveLength(0);
  });
});
