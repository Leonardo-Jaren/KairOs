import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import { describe, expect, it } from 'vitest';

import DashboardLayout from '@/layouts/DashboardLayout.vue';

const createWrapper = async () => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', component: { template: '<div />' } }],
  });
  await router.push('/');
  await router.isReady();

  return mount(DashboardLayout, {
    global: {
      plugins: [createPinia(), router],
    },
  });
};

describe('DashboardLayout', () => {
  it('permite cerrar y volver a abrir la barra lateral desde su encabezado', async () => {
    const wrapper = await createWrapper();
    const sidebar = wrapper.get('aside');

    await wrapper.get('[aria-label="Cerrar barra lateral"]').trigger('click');

    expect(sidebar.classes()).toContain('lg:w-0');
    expect(wrapper.find('[aria-label="Abrir barra lateral"]').exists()).toBe(true);

    await wrapper.get('[aria-label="Abrir barra lateral"]').trigger('click');

    expect(sidebar.classes()).toContain('lg:w-72');
    expect(wrapper.find('[aria-label="Abrir barra lateral"]').exists()).toBe(false);
  });
});
