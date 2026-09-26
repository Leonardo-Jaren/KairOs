import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import OrgChartNode from '@/components/organigrama/OrgChartNode.vue';

describe('OrgChartNode', () => {
  it('renderiza limpiamente usuario sin asignaciones territoriales (0 asignaciones)', () => {
    const node = {
      id: 1,
      nombre: 'Ada Admin',
      username: 'aadmin',
      rol: 'admin',
      is_active: true,
      sedes: [{ id: 1, nombre: 'Campus Central' }],
      asignaciones_territoriales: [],
      children: [],
    };

    const wrapper = mount(OrgChartNode, {
      props: { node },
    });

    const badges = wrapper.findAll('[data-testid="territorial-badge"]');
    expect(badges).toHaveLength(0);
    expect(wrapper.find('[data-testid="territorial-overflow"]').exists()).toBe(false);
    expect(wrapper.text()).toContain('Ada Admin');
    expect(wrapper.text()).toContain('Administrador');
  });

  it('soporta de forma defensiva nodo con asignaciones_territoriales indefinidas', () => {
    const node = {
      id: 2,
      nombre: 'Sin Asignaciones',
      rol: 'usuario',
      is_active: true,
    };

    const wrapper = mount(OrgChartNode, {
      props: { node },
    });

    expect(wrapper.findAll('[data-testid="territorial-badge"]')).toHaveLength(0);
  });

  it('renderiza 1 asignación a nivel Piso con icono Layers y estilo teal', () => {
    const node = {
      id: 3,
      nombre: 'Tomás Técnico',
      rol: 'tecnico',
      is_active: true,
      asignaciones_territoriales: [
        {
          id: 1,
          ambito: 'piso',
          badge_texto: 'Encargado Piso 2 · Pabellón A',
          tipo_responsabilidad: 'tecnico',
        },
      ],
      children: [],
    };

    const wrapper = mount(OrgChartNode, {
      props: { node },
    });

    const badges = wrapper.findAll('[data-testid="territorial-badge"]');
    expect(badges).toHaveLength(1);
    expect(badges[0].text()).toContain('Encargado Piso 2 · Pabellón A');
    expect(badges[0].classes()).toContain('bg-teal-50');
    expect(badges[0].classes()).toContain('text-teal-700');
    expect(wrapper.find('svg.lucide-layers').exists()).toBe(true);
    expect(wrapper.find('[data-testid="territorial-overflow"]').exists()).toBe(false);
  });

  it('renderiza 1 asignación a nivel Edificio con icono Building2 y estilo blue', () => {
    const node = {
      id: 4,
      nombre: 'Carlos Responsable',
      rol: 'responsable',
      is_active: true,
      asignaciones_territoriales: [
        {
          id: 2,
          ambito: 'edificio',
          badge_texto: 'Encargado Pabellón Central',
          tipo_responsabilidad: 'responsable',
        },
      ],
      children: [],
    };

    const wrapper = mount(OrgChartNode, {
      props: { node },
    });

    const badges = wrapper.findAll('[data-testid="territorial-badge"]');
    expect(badges).toHaveLength(1);
    expect(badges[0].text()).toContain('Encargado Pabellón Central');
    expect(badges[0].classes()).toContain('bg-blue-50');
    expect(badges[0].classes()).toContain('text-blue-700');
    expect(wrapper.find('svg.lucide-building-2').exists()).toBe(true);
  });

  it('renderiza 1 asignación a nivel Sede con icono Landmark y estilo indigo', () => {
    const node = {
      id: 5,
      nombre: 'Diana Directora',
      rol: 'responsable',
      is_active: true,
      asignaciones_territoriales: [
        {
          id: 3,
          ambito: 'sede',
          badge_texto: 'Responsable · Campus Central',
          tipo_responsabilidad: 'responsable',
        },
      ],
      children: [],
    };

    const wrapper = mount(OrgChartNode, {
      props: { node },
    });

    const badges = wrapper.findAll('[data-testid="territorial-badge"]');
    expect(badges).toHaveLength(1);
    expect(badges[0].text()).toContain('Responsable · Campus Central');
    expect(badges[0].classes()).toContain('bg-indigo-50');
    expect(badges[0].classes()).toContain('text-indigo-700');
    expect(wrapper.find('svg.lucide-landmark').exists()).toBe(true);
  });

  it('renderiza 1 asignación a nivel Espacio con icono DoorClosed y estilo purple', () => {
    const node = {
      id: 6,
      nombre: 'Eduardo Docente',
      rol: 'docente',
      is_active: true,
      asignaciones_territoriales: [
        {
          id: 4,
          ambito: 'espacio',
          badge_texto: 'LAB-201 · Pabellón Central',
          tipo_responsabilidad: 'docente',
        },
      ],
      children: [],
    };

    const wrapper = mount(OrgChartNode, {
      props: { node },
    });

    const badges = wrapper.findAll('[data-testid="territorial-badge"]');
    expect(badges).toHaveLength(1);
    expect(badges[0].text()).toContain('LAB-201 · Pabellón Central');
    expect(badges[0].classes()).toContain('bg-purple-50');
    expect(badges[0].classes()).toContain('text-purple-700');
    expect(wrapper.find('svg.lucide-door-closed').exists()).toBe(true);
  });

  it('gestiona múltiples asignaciones mostrando badge principal y pastilla de desbordamiento (+N)', () => {
    const node = {
      id: 7,
      nombre: 'Tomás Multi-Asignado',
      rol: 'tecnico',
      is_active: true,
      asignaciones_territoriales: [
        { id: 1, ambito: 'piso', badge_texto: 'Encargado Piso 1 · Pabellón A' },
        { id: 2, ambito: 'piso', badge_texto: 'Encargado Piso 2 · Pabellón A' },
        { id: 3, ambito: 'edificio', badge_texto: 'Encargado Pabellón B' },
      ],
      children: [],
    };

    const wrapper = mount(OrgChartNode, {
      props: { node },
    });

    const badges = wrapper.findAll('[data-testid="territorial-badge"]');
    expect(badges).toHaveLength(1);
    expect(badges[0].text()).toContain('Encargado Piso 1 · Pabellón A');

    const overflowPill = wrapper.find('[data-testid="territorial-overflow"]');
    expect(overflowPill.exists()).toBe(true);
    expect(overflowPill.text()).toContain('+2');
    expect(overflowPill.attributes('title')).toContain('Encargado Piso 2 · Pabellón A');
    expect(overflowPill.attributes('title')).toContain('Encargado Pabellón B');
  });

  it('emite select al hacer clic en la tarjeta del nodo', async () => {
    const node = {
      id: 10,
      nombre: 'Nodo Clickeable',
      rol: 'tecnico',
      is_active: true,
      children: [],
    };

    const wrapper = mount(OrgChartNode, {
      props: { node },
    });

    await wrapper.find('.group.relative').trigger('click');
    expect(wrapper.emitted('select')).toBeTruthy();
    expect(wrapper.emitted('select')[0][0].id).toBe(10);
  });

  it('emite toggle-collapse y manage-permisos al interactuar con los botones de acción', async () => {
    const node = {
      id: 11,
      nombre: 'Nodo con Hijos',
      rol: 'admin',
      is_active: true,
      children: [{ id: 12, nombre: 'Hijo', rol: 'tecnico', children: [] }],
    };

    const wrapper = mount(OrgChartNode, {
      props: { node },
    });

    const buttons = wrapper.findAll('button');
    const managePermBtn = buttons.find((b) => b.attributes('title') === 'Gestionar permisos');
    await managePermBtn.trigger('click');
    expect(wrapper.emitted('manage-permisos')).toBeTruthy();
    expect(wrapper.emitted('manage-permisos')[0][0].id).toBe(11);

    const collapseBtn = buttons.find((b) => b.attributes('title')?.includes('rama'));
    await collapseBtn.trigger('click');
    expect(wrapper.emitted('toggle-collapse')).toBeTruthy();
    expect(wrapper.emitted('toggle-collapse')[0][0]).toBe(11);
  });
});
