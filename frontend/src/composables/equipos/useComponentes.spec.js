import { flushPromises, mount } from '@vue/test-utils';
import { defineComponent, h } from 'vue';
import { describe, expect, it, vi } from 'vitest';

import { useComponentes } from '@/composables/equipos/useComponentes';

const original = {
  id: 272,
  equipo: 40,
  equipo_codigo: 'LAB201-PC040',
  tipo: 'cpu',
  tipo_display: 'CPU',
  modelo: 'Intel Core i5-12400',
  descripcion: '6 nucleos, hasta 4.4 GHz',
};

const updated = {
  ...original,
  tipo: 'ram',
  tipo_display: 'RAM',
};

const mountComposable = (service) => {
  let state;
  const wrapper = mount(defineComponent({
    setup() {
      state = useComponentes(service);
      return () => h('div');
    },
  }));
  return { state, wrapper };
};

describe('useComponentes', () => {
  it('envia filtros y conserva la paginacion devuelta por la API', async () => {
    const service = {
      listar: vi.fn().mockResolvedValue({ count: 241, results: [original] }),
    };
    const { state } = mountComposable(service);

    await state.cargar();

    expect(service.listar).toHaveBeenCalledWith({
      search: '',
      tipo: '',
      page: 1,
      page_size: 10,
    });
    expect(state.pagination.total).toBe(241);
    expect(state.pagination.totalPages).toBe(25);
  });

  it('reemplaza inmediatamente el componente editado sin perderlo del listado', async () => {
    const service = {
      listar: vi.fn().mockResolvedValue({ count: 241, results: [original] }),
      actualizar: vi.fn().mockResolvedValue(updated),
    };
    const { state } = mountComposable(service);
    await state.cargar();
    state.openEdit(original);
    state.form.tipo = 'ram';

    const result = await state.submit();
    await flushPromises();

    expect(result).toBe(true);
    expect(state.componentes.value[0]).toEqual(updated);
    expect(state.componentes.value[0].tipo_display).toBe('RAM');
    expect(service.listar).toHaveBeenCalledOnce();
  });
});
