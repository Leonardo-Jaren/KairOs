import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import { describe, expect, it } from 'vitest';

import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useAuthStore } from '@/stores/auth';

const createWrapper = async (user = null) => {
  const pinia = createPinia();
  setActivePinia(pinia);
  const authStore = useAuthStore();
  if (user) {
    authStore.user = user;
    authStore.accessToken = 'test-token';
  }

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/dashboard', component: { template: '<div />' } },
    ],
  });
  await router.push('/dashboard');
  await router.isReady();

  return mount(DashboardLayout, {
    global: {
      plugins: [pinia, router],
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

  it('muestra únicamente Dashboard, Software, Instalaciones e Incidencias para rol docente', async () => {
    const wrapper = await createWrapper({
      id: 1,
      nombre: 'Ana',
      apellido: 'Torres',
      rol: 'docente',
    });

    const links = wrapper.findAll('nav a');
    const linkTexts = links.map((l) => l.text().trim());

    // Debe contener únicamente los 4 módulos pedagógicos autorizados
    expect(linkTexts).toEqual(['Dashboard', 'Software', 'Instalaciones', 'Incidencias']);

    // Módulos de infraestructura y administración excluidos
    expect(linkTexts).not.toContain('Campus');
    expect(linkTexts).not.toContain('Croquis');
    expect(linkTexts).not.toContain('Espacios');
    expect(linkTexts).not.toContain('Usuarios por espacio');
    expect(linkTexts).not.toContain('Equipos');
    expect(linkTexts).not.toContain('Componentes');
    expect(linkTexts).not.toContain('Mantenimiento');
    expect(linkTexts).not.toContain('Historial');
    expect(linkTexts).not.toContain('Usuarios');
  });

  it('oculta tanto Software como Instalaciones si el modulo software no tiene permiso', async () => {
    const wrapper = await createWrapper({
      id: 1,
      nombre: 'Ana',
      apellido: 'Torres',
      rol: 'docente',
      permisos_efectivos: {
        software: { ver: false, crear: false, editar: false, eliminar: false },
        incidencias: { ver: true, crear: true, editar: true, eliminar: false },
      },
    });

    const links = wrapper.findAll('nav a');
    const linkTexts = links.map((l) => l.text().trim());

    expect(linkTexts).toEqual(['Dashboard', 'Incidencias']);
    expect(linkTexts).not.toContain('Software');
    expect(linkTexts).not.toContain('Instalaciones');
  });

  it('oculta Espacios y Usuarios por espacio si el modulo espacios no tiene permiso', async () => {
    const wrapper = await createWrapper({
      id: 2,
      nombre: 'Tomás',
      rol: 'tecnico',
      permisos_efectivos: {
        espacios: { ver: false, crear: false, editar: false, eliminar: false },
        equipos: { ver: true, crear: true, editar: true, eliminar: false },
      },
    });

    const links = wrapper.findAll('nav a');
    const linkTexts = links.map((l) => l.text().trim());

    expect(linkTexts).not.toContain('Campus');
    expect(linkTexts).not.toContain('Croquis');
    expect(linkTexts).not.toContain('Espacios');
    expect(linkTexts).not.toContain('Usuarios por espacio');
    expect(linkTexts).toContain('Equipos');
    expect(linkTexts).toContain('Componentes');
  });

  it('oculta Equipos y Componentes si el modulo equipos no tiene permiso', async () => {
    const wrapper = await createWrapper({
      id: 2,
      nombre: 'Tomás',
      rol: 'tecnico',
      permisos_efectivos: {
        equipos: { ver: false, crear: false, editar: false, eliminar: false },
        espacios: { ver: true, crear: false, editar: false, eliminar: false },
      },
    });

    const links = wrapper.findAll('nav a');
    const linkTexts = links.map((l) => l.text().trim());

    expect(linkTexts).not.toContain('Equipos');
    expect(linkTexts).not.toContain('Componentes');
    expect(linkTexts).toContain('Espacios');
  });

  it('permite ver submódulos de espacios a un docente si se le otorga permiso personalizado', async () => {
    const wrapper = await createWrapper({
      id: 1,
      nombre: 'Ana',
      rol: 'docente',
      permisos_efectivos: {
        espacios: { ver: true, crear: false, editar: false, eliminar: false },
      },
    });

    const links = wrapper.findAll('nav a');
    const linkTexts = links.map((l) => l.text().trim());

    // Debe incluir los submódulos dependientes de espacios
    expect(linkTexts).toContain('Espacios');
    expect(linkTexts).toContain('Croquis');
    expect(linkTexts).toContain('Usuarios por espacio');
    // Módulos base siguen disponibles
    expect(linkTexts).toContain('Software');
    expect(linkTexts).toContain('Incidencias');
    // Otros módulos sin permiso siguen ocultos
    expect(linkTexts).not.toContain('Equipos');
    expect(linkTexts).not.toContain('Mantenimiento');
  });

  it('muestra únicamente Dashboard, Software, Instalaciones e Incidencias para rol usuario', async () => {
    const wrapper = await createWrapper({
      id: 3,
      nombre: 'Carlos',
      rol: 'usuario',
    });

    const links = wrapper.findAll('nav a');
    const linkTexts = links.map((l) => l.text().trim());

    expect(linkTexts).toEqual(['Dashboard', 'Software', 'Instalaciones', 'Incidencias']);
  });
});

