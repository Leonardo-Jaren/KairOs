import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import BasePagination from '@/components/pagination/BasePagination.vue';

describe('BasePagination', () => {
  const mountPagination = (props = {}) => mount(BasePagination, {
    props: {
      page: 7,
      totalPages: 8,
      total: 80,
      ...props,
    },
  });

  it('permite escribir una página válida y navegar al enviarla', async () => {
    const wrapper = mountPagination();
    const input = wrapper.get('input[aria-label="Número de página"]');

    await input.setValue('5');
    await wrapper.get('form').trigger('submit');

    expect(wrapper.emitted('change')).toEqual([[5]]);
  });

  it('descarta caracteres que no sean números', async () => {
    const wrapper = mountPagination();
    const input = wrapper.get('input[aria-label="Número de página"]');

    await input.setValue('página 3x');

    expect(input.element.value).toBe('3');
  });

  it('mantiene la página actual cuando el número no existe', async () => {
    const wrapper = mountPagination();

    await wrapper.get('input[aria-label="Número de página"]').setValue('9');
    await wrapper.get('form').trigger('submit');

    expect(wrapper.emitted('change')).toBeUndefined();
    expect(wrapper.get('[role="alert"]').text()).toBe('La página debe estar entre 1 y 8.');
  });

  it('sincroniza el campo cuando cambia la página desde los controles', async () => {
    const wrapper = mountPagination();

    await wrapper.setProps({ page: 8 });

    expect(wrapper.get('input[aria-label="Número de página"]').element.value).toBe('8');
  });
});
