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
  it('permite contraer y expandir la barra lateral desde su encabezado', async () => {
    const wrapper = await createWrapper();
    const sidebar = wrapper.get('aside');

    await wrapper.get('[aria-label="Contraer barra lateral"]').trigger('click');

    expect(sidebar.classes()).toContain('lg:w-20');
    expect(wrapper.find('[aria-label="Expandir barra lateral"]').exists()).toBe(true);
    expect(wrapper.get('nav').classes()).toContain('lg:px-3');

    await wrapper.get('[aria-label="Expandir barra lateral"]').trigger('click');

    expect(sidebar.classes()).toContain('lg:w-72');
    expect(wrapper.find('[aria-label="Expandir barra lateral"]').exists()).toBe(false);
  });
});
