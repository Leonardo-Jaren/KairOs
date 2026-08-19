import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import CroquisPiso from '@/components/espacios/CroquisPiso.vue';

const createFloor = () => ({
  key: '2',
  label: 'Piso 2',
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
    },
    {
      id: 2,
      codigo_espacio: 'LAB-202',
      tipo: 'sala_computo',
      tipo_display: 'Sala de cómputo',
      cantidad_equipos: 8,
      resumen_equipos: { dañado: 0, en_mantenimiento: 1 },
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
});
