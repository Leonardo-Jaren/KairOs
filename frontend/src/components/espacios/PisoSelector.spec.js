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
});
