import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import BaseTable from '@/components/tables/BaseTable.vue';

describe('BaseTable', () => {
  const columns = [{ key: 'nombre', label: 'Nombre' }];

  it('renderiza filas y permite personalizar celdas', () => {
    const wrapper = mount(BaseTable, {
      props: { columns, items: [{ id: 1, nombre: 'Diana' }] },
      slots: { 'cell-nombre': '<strong>Usuario personalizado</strong>' },
    });

    expect(wrapper.text()).toContain('Usuario personalizado');
    expect(wrapper.findAll('tbody tr')).toHaveLength(1);
  });

  it('muestra un estado vacío descriptivo', () => {
    const wrapper = mount(BaseTable, {
      props: { columns, items: [], emptyMessage: 'Sin usuarios.' },
    });

    expect(wrapper.text()).toContain('Sin usuarios.');
  });

  it('conserva las filas mientras actualiza datos ya cargados', () => {
    const wrapper = mount(BaseTable, {
      props: {
        columns,
        items: [{ id: 1, nombre: 'Diana' }],
        loading: true,
      },
    });

    expect(wrapper.text()).toContain('Diana');
    expect(wrapper.text()).toContain('Actualizando registros...');
    expect(wrapper.findAll('tbody tr')).toHaveLength(1);
  });
});
