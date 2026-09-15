import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import LoginView from '@/views/auth/LoginView.vue';

// Mock de servicios externos de Google para entorno de pruebas
vi.mock('@/services/google-identity.service', () => ({
  renderGoogleButton: vi.fn().mockResolvedValue(undefined),
}));

const createWrapper = async () => {
  const pinia = createPinia();
  setActivePinia(pinia);

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/auth/login', component: LoginView },
      { path: '/auth/password-reset', component: { template: '<div />' } },
      { path: '/dashboard', component: { template: '<div />' } },
    ],
  });
  await router.push('/auth/login');
  await router.isReady();

  return mount(LoginView, {
    global: {
      plugins: [pinia, router],
    },
  });
};

describe('LoginView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renderiza correctamente el encabezado de portal institucional y los campos de entrada', async () => {
    const wrapper = await createWrapper();

    expect(wrapper.text()).toContain('Acceso a Laboratorios');
    expect(wrapper.text()).toContain('Portal Institucional KairOs');
    expect(wrapper.find('input#correo').exists()).toBe(true);
    expect(wrapper.find('input#password').exists()).toBe(true);
    expect(wrapper.find('button#btn-iniciar').exists()).toBe(true);
  });

  it('permite alternar la visibilidad de la contraseña con el botón de ojo', async () => {
    const wrapper = await createWrapper();
    const passwordInput = wrapper.get('input#password');

    expect(passwordInput.attributes('type')).toBe('password');

    const toggleBtn = wrapper.get('button[aria-label="Ver contraseña"]');
    await toggleBtn.trigger('click');

    expect(passwordInput.attributes('type')).toBe('text');

    const hideBtn = wrapper.get('button[aria-label="Ocultar contraseña"]');
    await hideBtn.trigger('click');

    expect(passwordInput.attributes('type')).toBe('password');
  });

  it('muestra error de validación cuando los campos se envían vacíos', async () => {
    const wrapper = await createWrapper();

    await wrapper.get('form').trigger('submit.prevent');

    expect(wrapper.text()).toContain('Por favor complete todos los campos');
  });

  it('muestra error de validación ante un formato de correo inválido', async () => {
    const wrapper = await createWrapper();

    await wrapper.get('input#correo').setValue('correo-invalido');
    await wrapper.get('input#password').setValue('Password123!');
    await wrapper.get('form').trigger('submit.prevent');

    expect(wrapper.text()).toContain('El formato del correo electronico no es valido');
  });

  it('contiene el enlace hacia la recuperación de contraseña', async () => {
    const wrapper = await createWrapper();
    const resetLink = wrapper.get('a[href="/auth/password-reset"]');

    expect(resetLink.text()).toContain('¿Olvidaste tu contraseña?');
  });

  it('restaura el correo guardado desde localStorage si existe', async () => {
    localStorage.setItem('kairos_remembered_email', 'admin@universidad.edu');
    const wrapper = await createWrapper();

    const correoInput = wrapper.get('input#correo');
    expect(correoInput.element.value).toBe('admin@universidad.edu');
    localStorage.removeItem('kairos_remembered_email');
  });

  it('limpia automáticamente el error de validación cuando el usuario escribe en un campo', async () => {
    const wrapper = await createWrapper();

    // Provocar error por campos vacíos
    await wrapper.get('form').trigger('submit.prevent');
    expect(wrapper.text()).toContain('Por favor complete todos los campos');

    // El usuario empieza a escribir en el correo
    await wrapper.get('input#correo').setValue('nuevo@institucion.edu');
    expect(wrapper.text()).not.toContain('Por favor complete todos los campos');
  });
});
