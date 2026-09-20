import { mount } from '@vue/test-utils';
import { afterEach, describe, expect, it } from 'vitest';

import OrgActionDock from '@/components/organigrama/OrgActionDock.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';

describe('OrgActionDock.vue', () => {
  afterEach(() => {
    document.documentElement.style.overflow = '';
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
  });

  const sinSupervisorMock = [
    {
      id: 10,
      nombre: 'Pedro',
      apellido: 'Perez',
      username: 'pperez',
      correo: 'pperez@example.com',
      rol: 'tecnico',
      sedes: [{ id: 1, nombre: 'Campus Central' }],
    },
  ];

  const docentesMock = [
    {
      id: 20,
      nombre: 'Maria',
      apellido: 'Docente',
      username: 'mdocente',
      correo: 'mdocente@example.com',
      rol: 'docente',
      sedes: [{ id: 1, nombre: 'Campus Central' }],
    },
  ];

  const supervisoresMock = [
    { id: 1, nombre: 'Ada Admin', rol: 'admin' },
  ];

  it('no renderiza contenido visible si open es false', () => {
    const wrapper = mount(OrgActionDock, {
      props: {
        open: false,
        sinSupervisor: sinSupervisorMock,
        docentes: docentesMock,
      },
    });

    expect(wrapper.find('aside').exists()).toBe(false);
  });

  it('renderiza tarjetas de personal sin supervisor y permite emitir asignacion', async () => {
    const wrapper = mount(OrgActionDock, {
      props: {
        open: true,
        sinSupervisor: sinSupervisorMock,
        docentes: docentesMock,
        supervisores: supervisoresMock,
      },
      global: { stubs: { Teleport: true } },
    });

    expect(wrapper.text()).toContain('Pedro Perez');
    expect(wrapper.text()).toContain('Campus Central');

    // Seleccionar supervisor en BaseSelect
    const baseSelect = wrapper.findComponent(BaseSelect);
    expect(baseSelect.exists()).toBe(true);
    baseSelect.vm.$emit('update:modelValue', 1);
    await wrapper.vm.$nextTick();

    // Presionar boton asignar
    const assignBtn = wrapper.find('button.bg-primary-600');
    expect(assignBtn.attributes('disabled')).toBeUndefined();
    await assignBtn.trigger('click');

    expect(wrapper.emitted('assign-supervisor')).toBeTruthy();
    expect(wrapper.emitted('assign-supervisor')[0]).toEqual([{ usuarioId: 10, supervisorId: 1 }]);
  });

  it('conmuta a la pestana de docentes y permite abrir ficha y permisos', async () => {
    const wrapper = mount(OrgActionDock, {
      props: {
        open: true,
        activeTab: 'docentes',
        sinSupervisor: sinSupervisorMock,
        docentes: docentesMock,
      },
      global: { stubs: { Teleport: true } },
    });

    expect(wrapper.text()).toContain('Maria Docente');

    // Clic en ver ficha
    const buttons = wrapper.findAll('button');
    const eyeBtn = buttons.find((b) => b.attributes('title') === 'Ver ficha técnica');
    expect(eyeBtn).toBeDefined();
    await eyeBtn.trigger('click');

    expect(wrapper.emitted('select')).toBeTruthy();
    expect(wrapper.emitted('select')[0][0].id).toBe(20);

    // Clic en permisos
    const permisosBtn = buttons.find((b) => b.attributes('title') === 'Configurar permisos');
    expect(permisosBtn).toBeDefined();
    await permisosBtn.trigger('click');

    expect(wrapper.emitted('manage-permisos')).toBeTruthy();
    expect(wrapper.emitted('manage-permisos')[0][0].id).toBe(20);
  });

  it('emite evento close al hacer clic en boton cerrar', async () => {
    const wrapper = mount(OrgActionDock, {
      props: {
        open: true,
        sinSupervisor: sinSupervisorMock,
        docentes: docentesMock,
      },
      global: { stubs: { Teleport: true } },
    });

    const closeBtn = wrapper.find('button[title="Cerrar panel lateral"]');
    await closeBtn.trigger('click');

    expect(wrapper.emitted('close')).toBeTruthy();
  });

  it('normaliza supervisores en formato value/label y permite seleccionarlos', async () => {
    const wrapper = mount(OrgActionDock, {
      props: {
        open: true,
        sinSupervisor: sinSupervisorMock,
        supervisores: [
          { value: 5, label: 'Carlos Responsable (responsable)' },
        ],
      },
      global: { stubs: { Teleport: true } },
    });

    const baseSelect = wrapper.findComponent(BaseSelect);
    expect(baseSelect.exists()).toBe(true);
    expect(baseSelect.props('options')).toEqual(
      expect.arrayContaining([expect.objectContaining({ label: expect.stringContaining('Carlos Responsable') })])
    );

    baseSelect.vm.$emit('update:modelValue', 5);
    await wrapper.vm.$nextTick();

    const assignBtn = wrapper.find('button.bg-primary-600');
    expect(assignBtn.attributes('disabled')).toBeUndefined();
    await assignBtn.trigger('click');

    expect(wrapper.emitted('assign-supervisor')).toBeTruthy();
    expect(wrapper.emitted('assign-supervisor')[0]).toEqual([{ usuarioId: 10, supervisorId: 5 }]);
  });

  it('deshabilita inputs y muestra spinner cuando assigningUserId coincide', () => {
    const wrapper = mount(OrgActionDock, {
      props: {
        open: true,
        sinSupervisor: sinSupervisorMock,
        supervisores: supervisoresMock,
        assigningUserId: 10,
      },
      global: { stubs: { Teleport: true } },
    });

    const baseSelect = wrapper.findComponent(BaseSelect);
    expect(baseSelect.props('disabled')).toBe(true);

    const assignBtn = wrapper.find('button.bg-primary-600');
    expect(assignBtn.attributes('disabled')).toBeDefined();
    expect(wrapper.find('.animate-spin').exists()).toBe(true);
  });

  it('renderiza cuadricula compacta en la pestana de docentes', () => {
    const wrapper = mount(OrgActionDock, {
      props: {
        open: true,
        activeTab: 'docentes',
        docentes: docentesMock,
      },
    });

    const grid = wrapper.find('.grid.grid-cols-1.sm\\:grid-cols-2');
    expect(grid.exists()).toBe(true);
    expect(wrapper.text()).toContain('Maria Docente');
    expect(wrapper.text()).toContain('Campus Central');
  });

  it('configura aside y contenedor interno con clases para scroll vertical fluido', () => {
    const wrapper = mount(OrgActionDock, {
      props: {
        open: true,
        sinSupervisor: sinSupervisorMock,
        docentes: docentesMock,
      },
    });

    const aside = wrapper.find('aside');
    expect(aside.classes()).toContain('h-full');
    expect(aside.classes()).toContain('max-h-screen');
    expect(aside.classes()).toContain('cursor-default');
    expect(aside.classes()).toContain('select-auto');

    const scrollContainer = wrapper.find('.overflow-y-auto');
    expect(scrollContainer.exists()).toBe(true);
    expect(scrollContainer.classes()).toContain('min-h-0');
    expect(scrollContainer.classes()).toContain('flex-1');
    expect(scrollContainer.classes()).toContain('dock-scrollbar');
    expect(scrollContainer.classes()).toContain('pb-8');
  });

  it('bloquea el scroll general mientras el panel esta abierto y lo restaura al cerrar', async () => {
    const wrapper = mount(OrgActionDock, {
      props: {
        open: false,
        sinSupervisor: sinSupervisorMock,
        docentes: docentesMock,
      },
    });

    await wrapper.setProps({ open: true });
    expect(document.documentElement.style.overflow).toBe('hidden');
    expect(document.body.style.overflow).toBe('hidden');

    await wrapper.setProps({ open: false });
    expect(document.documentElement.style.overflow).toBe('');
    expect(document.body.style.overflow).toBe('');

    wrapper.unmount();
  });
});
