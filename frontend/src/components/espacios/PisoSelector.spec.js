import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import PisoSelector from '@/components/espacios/PisoSelector.vue';

const floors = [
  { key: '1', label: 'Piso 1', aulas: 1, labs: 1, allSpaces: [{}, {}] },
  { key: '2', label: 'Piso 2', aulas: 0, labs: 2, allSpaces: [{}, {}] },
  { key: '3', label: 'Piso 3', aulas: 2, labs: 0, allSpaces: [{}, {}] },
];

describe('PisoSelector', () => {
  it('distribuye los pisos en una cuadrícula sin carril horizontal', async () => {
    const wrapper = mount(PisoSelector, {
      props: { floors, selectedKey: '1' },
    });

    const list = wrapper.get('[role="list"]');
    expect(list.classes()).toContain('grid');
    expect(list.classes()).not.toContain('overflow-x-auto');
    expect(wrapper.findAll('button')).toHaveLength(3);

    await wrapper.findAll('button')[1].trigger('click');
    expect(wrapper.emitted('select')).toEqual([['2']]);
  });

  it('renderiza el banner hero corporativo del pabellón con métricas y emite eventos de retorno y creación', async () => {
    const edificio = {
      id: 10,
      nombre: 'Pabellón 2',
      codigo: 'PAB-02',
      descripcion: 'Edificio de tecnología',
      pisos: ['1', '2'],
      spaces: [{ id: 1 }, { id: 2 }],
      equipos: 48,
    };

    const wrapper = mount(PisoSelector, {
      props: {
        edificio,
        localName: 'Sede La Esperanza',
        floors,
        canEdit: true,
      },
    });

    expect(wrapper.text()).toContain('Pabellón 2');
    expect(wrapper.text()).toContain('Sede La Esperanza');
    expect(wrapper.text()).toContain('PAB-02');
    expect(wrapper.text()).toContain('2 Pisos');
    expect(wrapper.text()).toContain('2 Ambientes');
    expect(wrapper.text()).toContain('48 Equipos');

    // Boton de retorno
    const backBtn = wrapper.findAll('button').find((b) => b.text().includes('Volver a pabellones'));
    expect(backBtn).toBeDefined();
    await backBtn.trigger('click');
    expect(wrapper.emitted('back')).toHaveLength(1);

    // Boton de agregar ambiente
    const createBtn = wrapper.findAll('button').find((b) => b.text().includes('Agregar ambiente'));
    expect(createBtn).toBeDefined();
    await createBtn.trigger('click');
    expect(wrapper.emitted('create-space')).toHaveLength(1);
  });

  it('muestra telemetría calculada para pisos con hardware monitoreado', () => {
    const floorsWithTelemetry = [
      {
        key: '1',
        label: 'Piso 1',
        allSpaces: [
          { id: 1, codigo_espacio: 'LAB-101', tipo: 'laboratorio', cantidad_equipos: 20, resumen_equipos: { en_mantenimiento: 2, dañado: 1 } },
        ],
      },
    ];

    const wrapper = mount(PisoSelector, {
      props: { floors: floorsWithTelemetry },
    });

    expect(wrapper.text()).toContain('LAB-101');
    expect(wrapper.text()).toContain('20 PCs');
    expect(wrapper.text()).toContain('17 operativos');
    expect(wrapper.text()).toContain('2 en mantenimiento');
    expect(wrapper.text()).toContain('1 incidencias');
  });

  it('muestra estado vacío amigable cuando el pabellón no tiene pisos', async () => {
    const wrapper = mount(PisoSelector, {
      props: { floors: [], canEdit: true },
    });

    expect(wrapper.text()).toContain('No hay pisos registrados en este pabellón');
    const emptyBtn = wrapper.get('button');
    expect(emptyBtn.text()).toContain('Registrar ambiente en Piso 1');
    await emptyBtn.trigger('click');
    expect(wrapper.emitted('create-space')).toHaveLength(1);
  });
});
