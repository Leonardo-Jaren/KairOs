import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import BaseSelect from '@/components/selects/BaseSelect.vue';

describe('BaseSelect', () => {
  const mountSelect = (props) => mount(BaseSelect, {
    props,
    global: { stubs: { Teleport: true } },
  });

  it('emite el valor seleccionado y muestra errores accesibles', async () => {
    const wrapper = mountSelect({
      id: 'role',
      modelValue: '',
      label: 'Rol',
      error: 'Selecciona un rol.',
      options: [{ value: 'admin', label: 'Administrador' }],
    });

    await wrapper.get('button[role="combobox"]').trigger('click');
    await wrapper.get('[role="option"]').trigger('click');

    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['admin']);
    expect(wrapper.get('[role="alert"]').text()).toBe('Selecciona un rol.');
  });

  it('muestra la opcion activa, permite navegar con teclado y cierra al escapar', async () => {
    const wrapper = mountSelect({
      id: 'type',
      modelValue: 'office',
      options: [
        { value: 'lab', label: 'Laboratorio' },
        { value: 'office', label: 'Oficina' },
      ],
    });

    const trigger = wrapper.get('button[role="combobox"]');
    expect(trigger.text()).toContain('Oficina');

    await trigger.trigger('keydown', { key: 'ArrowDown' });
    expect(wrapper.get('[role="listbox"]')).toBeTruthy();
    expect(wrapper.get('[role="option"]:nth-child(2)').attributes('aria-selected')).toBe('true');

    await trigger.trigger('keydown', { key: 'Escape' });
    expect(wrapper.find('[role="listbox"]').exists()).toBe(false);
  });

  it('conserva tipos no textuales de las opciones', async () => {
    const wrapper = mountSelect({
      id: 'user',
      modelValue: '',
      options: [{ value: 42, label: 'Diana' }],
    });

    await wrapper.get('button[role="combobox"]').trigger('click');
    await wrapper.get('[role="option"]').trigger('click');

    expect(wrapper.emitted('update:modelValue')[0]).toEqual([42]);
  });

  it('renderiza el menu fuera del contenedor para evitar scroll en modales', async () => {
    const host = document.createElement('div');
    document.body.appendChild(host);
    const wrapper = mount(BaseSelect, {
      attachTo: host,
      props: {
        id: 'modal-select',
        modelValue: '',
        options: [{ value: 'lab', label: 'Laboratorio' }],
      },
    });

    await wrapper.get('button[role="combobox"]').trigger('click');
    const menu = document.body.querySelector('#modal-select-options');

    expect(menu).not.toBeNull();
    expect(wrapper.element.contains(menu)).toBe(false);

    wrapper.unmount();
    host.remove();
  });
});
