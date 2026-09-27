import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import PlanoEspacioSkeleton from '@/components/espacios/PlanoEspacioSkeleton.vue';

describe('PlanoEspacioSkeleton', () => {
  it('renderiza el contenedor principal accesible con atributos de estado', () => {
    const wrapper = mount(PlanoEspacioSkeleton);

    const container = wrapper.get('[role="status"]');
    expect(container.attributes('aria-busy')).toBe('true');
    expect(container.attributes('aria-label')).toBe('Cargando plano interactivo del salón');
  });

  it('renderiza las 4 tarjetas de métricas del salón', () => {
    const wrapper = mount(PlanoEspacioSkeleton);

    const articles = wrapper.findAll('header section article');
    expect(articles).toHaveLength(4);
  });

  it('renderiza el banner del frente del aula y las celdas por defecto (6 columnas x 3 filas = 18 celdas)', () => {
    const wrapper = mount(PlanoEspacioSkeleton);

    expect(wrapper.text()).toContain('Frente del aula');
    expect(wrapper.text()).toContain('Docente');
    expect(wrapper.text()).toContain('Pasillo');

    // Por defecto 6 columnas x 3 filas = 18 celdas
    const cells = wrapper.findAll('.min-h-27');
    expect(cells).toHaveLength(18);
  });

  it('adapta la cantidad de celdas según las props de filas y columnas', () => {
    const wrapper = mount(PlanoEspacioSkeleton, {
      props: {
        columns: 4,
        rows: 2,
      },
    });

    // 4 columnas x 2 filas = 8 celdas
    const cells = wrapper.findAll('.min-h-27');
    expect(cells).toHaveLength(8);
  });
});
