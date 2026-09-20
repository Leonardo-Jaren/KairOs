import { mount } from '@vue/test-utils';
import { afterEach, describe, expect, it, vi } from 'vitest';

import OrgChartTree from '@/components/organigrama/OrgChartTree.vue';

describe('OrgChartTree.vue', () => {
  const originalMatchMedia = window.matchMedia;

  afterEach(() => {
    vi.unstubAllGlobals();
    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      writable: true,
      value: originalMatchMedia,
    });
  });

  const treeNodeWithChildren = {
    id: 1,
    nombre: 'Ana',
    apellido: 'Torres',
    nombre_completo: 'Ana Torres',
    rol: 'superadmin',
    children: [
      {
        id: 2,
        nombre: 'Carlos',
        apellido: 'Mendoza',
        nombre_completo: 'Carlos Mendoza',
        rol: 'admin',
        children: [],
      },
    ],
  };

  const independentNode = {
    id: 3,
    nombre: 'Elena',
    apellido: 'Gomez',
    nombre_completo: 'Elena Gomez',
    rol: 'tecnico',
    children: [],
  };

  const defaultProps = {
    arbol: [treeNodeWithChildren, independentNode],
    rawArbol: [treeNodeWithChildren, independentNode],
    grupos: {
      arbol_mando: [treeNodeWithChildren],
      sin_supervisor: [independentNode],
      docentes: [],
      sin_sede: [],
    },
    meta: {
      total: 2,
      total_mando: 2,
      total_sin_supervisor: 1,
      total_docentes: 0,
    },
    activeView: 'mando',
    zoom: 1,
    pan: { x: 0, y: 0 },
    isDragging: false,
    collapsedNodes: new Set(),
    zoomIn: vi.fn(),
    zoomOut: vi.fn(),
    resetView: vi.fn(),
    expandAll: vi.fn(),
    collapseAll: vi.fn(),
    toggleCollapse: vi.fn(),
    onMouseDown: vi.fn(),
    onMouseMove: vi.fn(),
    onMouseUp: vi.fn(),
    onWheel: vi.fn(),
  };

  it('renderiza vista Linea de Mando con arbol centrado por defecto', () => {
    const wrapper = mount(OrgChartTree, {
      props: {
        ...defaultProps,
        activeView: 'mando',
      },
    });

    // En mando, renderiza el contenedor flex tradicional centrado
    expect(wrapper.find('.mx-auto.flex.items-start.justify-center').classes()).toContain('w-max');
    expect(wrapper.text()).toContain('Ana Torres');
  });

  it('renderiza vista Todos con cuadricula en columnas para nodos independientes', async () => {
    const resetViewMock = vi.fn();
    const wrapper = mount(OrgChartTree, {
      props: {
        ...defaultProps,
        activeView: 'todos',
        resetView: resetViewMock,
      },
    });

    // En vista todos, los nodos independientes se ubican en grid responsivo de columnas
    const grid = wrapper.find('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3.xl\\:grid-cols-4');
    expect(grid.exists()).toBe(true);
    expect(grid.text()).toContain('Elena Gomez');

    // El arbol con subordinados se renderiza en la seccion superior
    expect(wrapper.text()).toContain('Ana Torres');
    expect(wrapper.text()).toContain('Colaboradores Independientes (1)');
  });

  it('emite change-view y llama a resetView al hacer clic en el boton Todos', async () => {
    const resetViewMock = vi.fn();
    const wrapper = mount(OrgChartTree, {
      props: {
        ...defaultProps,
        resetView: resetViewMock,
      },
    });

    const btnTodos = wrapper.findAll('button').find((b) => b.text().includes('Todos'));
    expect(btnTodos).toBeDefined();
    await btnTodos.trigger('click');

    expect(wrapper.emitted('change-view')).toBeTruthy();
    expect(wrapper.emitted('change-view')[0]).toEqual(['todos']);
    expect(resetViewMock).toHaveBeenCalled();
  });

  it('permite alternar el dock de accion rapida', async () => {
    const wrapper = mount(OrgChartTree, {
      props: defaultProps,
    });

    const dockBtn = wrapper.find('button[title="Alternar panel lateral de accion rapida"]');
    expect(dockBtn.exists()).toBe(true);
    await dockBtn.trigger('click');

    expect(wrapper.emitted('open-dock')).toBeTruthy();
  });

  it('conserva amplitud panoramica en escritorio y transition-none durante el arrastre', () => {
    const wrapper = mount(OrgChartTree, {
      props: {
        ...defaultProps,
        activeView: 'todos',
        isDragging: true,
      },
    });

    // Contenedor principal de Todos debe tener min-w-max para no colapsar columnas
    const todosContainer = wrapper.findAll('div').find((element) => element.classes().includes('md:min-w-max'));
    expect(todosContainer).toBeDefined();

    // Durante arrastre, la capa del lienzo debe tener transition-none para movimiento instantaneo
    const canvasLayer = wrapper.find('.transition-none');
    expect(canvasLayer.exists()).toBe(true);
  });

  it('conserva el lienzo interactivo fluido con transformaciones y overflow-hidden estricto', () => {
    const wrapper = mount(OrgChartTree, {
      props: {
        ...defaultProps,
        pan: { x: 80, y: 40 },
        zoom: 0.75,
      },
    });

    const container = wrapper.get('[data-testid="org-chart"]');
    const canvas = wrapper.get('[data-testid="org-chart-canvas"]');
    const roots = wrapper.find('.mx-auto.flex.items-start.justify-center');

    expect(canvas.attributes('style')).toContain('translate(80px, 40px) scale(0.75)');
    expect(container.classes()).toContain('overflow-hidden');
    expect(container.classes()).not.toContain('overflow-y-auto');
    expect(roots.classes()).toContain('w-max');
    expect(roots.classes()).not.toContain('flex-col');
  });

  it('renderiza boton de exportacion a PNG y expone el metodo exportToPng', () => {
    const wrapper = mount(OrgChartTree, {
      props: defaultProps,
    });

    const exportBtn = wrapper.find('button[title="Exportar organigrama como imagen PNG en alta resolución"]');
    expect(exportBtn.exists()).toBe(true);
    expect(exportBtn.text()).toContain('PNG');

    // Verifica que el componente expone la función exportToPng
    expect(typeof wrapper.vm.exportToPng).toBe('function');
  });
});
