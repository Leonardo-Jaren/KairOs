import { mount } from '@vue/test-utils';
import { defineComponent, h, reactive } from 'vue';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { useAutoFilters } from '@/composables/shared/useAutoFilters';

const mountFilters = (load) => {
  let state;
  const wrapper = mount(defineComponent({
    setup() {
      const filters = reactive({ search: '', estado: '', page: 4 });
      const controls = useAutoFilters(filters, load, {
        immediateKeys: ['estado'],
        delay: 350,
      });
      state = { filters, ...controls };
      return () => h('div');
    },
  }));

  return { state, wrapper };
};

describe('useAutoFilters', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('espera antes de buscar y usa solamente el último texto', async () => {
    vi.useFakeTimers();
    const load = vi.fn();
    const { state } = mountFilters(load);

    state.filters.search = 'la';
    await Promise.resolve();
    state.filters.search = 'laptop';
    await Promise.resolve();
    await vi.advanceTimersByTimeAsync(349);
    expect(load).not.toHaveBeenCalled();

    await vi.advanceTimersByTimeAsync(1);
    expect(load).toHaveBeenCalledOnce();
    expect(state.filters.page).toBe(1);
  });

  it('aplica los filtros de selección inmediatamente', async () => {
    const load = vi.fn();
    const { state } = mountFilters(load);

    state.filters.estado = 'activo';
    await Promise.resolve();

    expect(load).toHaveBeenCalledOnce();
    expect(state.filters.page).toBe(1);
  });

  it('limpia los filtros con una sola recarga', async () => {
    const load = vi.fn();
    const { state } = mountFilters(load);
    state.filters.search = 'equipo';
    state.filters.estado = 'activo';
    await Promise.resolve();
    load.mockClear();

    await state.resetFilters({ search: '', estado: '' });

    expect(load).toHaveBeenCalledOnce();
    expect(state.filters).toMatchObject({ search: '', estado: '', page: 1 });
  });
});
