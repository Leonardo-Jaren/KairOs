import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import PabellonAxonometrico from '@/components/espacios/PabellonAxonometrico.vue';

describe('PabellonAxonometrico', () => {
  it('dibuja una fachada por cada piso y etiqueta sus ventanas', () => {
    const wrapper = mount(PabellonAxonometrico, {
      props: {
        name: 'Pabellón Académico',
        floors: 3,
      },
    });

    expect(wrapper.get('svg').attributes('aria-labelledby')).toBeTruthy();
    expect(wrapper.get('title').text()).toBe('Pabellón Académico, edificio de 3 pisos');
    expect(wrapper.findAll('[data-floor-level]')).toHaveLength(3);
    expect(wrapper.findAll('[data-window]')).toHaveLength(18);
  });

  it('indica cuando el pabellón aún no tiene pisos registrados', () => {
    const wrapper = mount(PabellonAxonometrico, {
      props: {
        name: 'Pabellón Administrativo',
        floors: 0,
      },
    });

    expect(wrapper.get('svg title').text()).toBe('Pabellón Administrativo, sin pisos registrados');
    expect(wrapper.text()).toContain('Sin pisos registrados');
    expect(wrapper.findAll('[data-floor-level]')).toHaveLength(0);
    expect(wrapper.findAll('[data-window]')).toHaveLength(0);
  });

  it('resalta el pabellón seleccionado', () => {
    const wrapper = mount(PabellonAxonometrico, {
      props: { floors: 2, selected: true },
    });

    expect(wrapper.get('svg').classes()).toContain('is-selected');
  });
});
