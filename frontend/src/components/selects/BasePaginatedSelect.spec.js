import { flushPromises, mount } from '@vue/test-utils';
import { afterEach, describe, expect, it, vi } from 'vitest';

import BasePaginatedSelect from '@/components/selects/BasePaginatedSelect.vue';

const mountSelect = (props) => mount(BasePaginatedSelect, {
  props,
  global: { stubs: { Teleport: true } },
});

afterEach(() => {
  vi.useRealTimers();
});

describe('BasePaginatedSelect', () => {
  it('carga la primera página y conserva el tipo del valor seleccionado', async () => {
    const loadOptions = vi.fn().mockResolvedValue({
      options: [{ value: 21, label: 'Diana Docente' }],
      total: 15,
    });
    const wrapper = mountSelect({
      id: 'users',
      modelValue: '',
      loadOptions,
    });

    await wrapper.get('button[role="combobox"]').trigger('click');
    await flushPromises();

    expect(loadOptions).toHaveBeenCalledWith({ page: 1, pageSize: 10, search: '' });
    expect(wrapper.text()).toContain('15 registros');
    await wrapper.get('[role="option"]').trigger('click');
    expect(wrapper.emitted('update:modelValue')[0]).toEqual([21]);
    wrapper.unmount();
  });

  it('solicita la página siguiente sin cargar todas las opciones', async () => {
    const loadOptions = vi.fn().mockImplementation(({ page }) => Promise.resolve({
      options: [{ value: page, label: `Página ${page}` }],
      total: 12,
    }));
    const wrapper = mountSelect({
      id: 'spaces',
      modelValue: '',
      loadOptions,
    });

    await wrapper.get('button[role="combobox"]').trigger('click');
    await flushPromises();
    await wrapper.get('[aria-label="Página siguiente de opciones"]').trigger('click');
    await flushPromises();

    expect(loadOptions).toHaveBeenLastCalledWith({ page: 2, pageSize: 10, search: '' });
    expect(wrapper.text()).toContain('Página 2');
    wrapper.unmount();
  });

  it('reinicia la paginación al buscar con espera controlada', async () => {
    vi.useFakeTimers();
    const loadOptions = vi.fn().mockResolvedValue({ options: [], total: 0 });
    const wrapper = mountSelect({
      id: 'searchable-users',
      modelValue: '',
      loadOptions,
      searchPlaceholder: 'Buscar usuario',
    });

    await wrapper.get('button[role="combobox"]').trigger('click');
    await flushPromises();
    await wrapper.get('input[type="search"]').setValue('Diana');
    await vi.advanceTimersByTimeAsync(300);
    await flushPromises();

    expect(loadOptions).toHaveBeenLastCalledWith({ page: 1, pageSize: 10, search: 'Diana' });
    wrapper.unmount();
  });

  it('muestra una opción inicial aunque no pertenezca a la página cargada', () => {
    const wrapper = mountSelect({
      id: 'editing-user',
      modelValue: 7,
      initialOption: { value: 7, label: 'Usuario existente' },
      loadOptions: vi.fn(),
    });

    expect(wrapper.get('button[role="combobox"]').text()).toContain('Usuario existente');
    wrapper.unmount();
  });
});
