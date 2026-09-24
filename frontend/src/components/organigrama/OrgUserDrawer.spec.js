import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, it } from 'vitest';

import OrgUserDrawer from '@/components/organigrama/OrgUserDrawer.vue';
import { useAuthStore } from '@/stores/auth';

const mountDrawer = (props = {}, authUser = null) => {
  const pinia = createPinia();
  setActivePinia(pinia);
  const authStore = useAuthStore();
  if (authUser) {
    authStore.user = authUser;
  }
  return mount(OrgUserDrawer, {
    props: {
      open: true,
      ...props,
    },
    global: {
      plugins: [pinia],
      stubs: {
        Teleport: true,
        BaseButton: false,
      },
    },
  });
};

describe('OrgUserDrawer', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('muestra estado vacío cuando el usuario no tiene asignaciones territoriales', () => {
    const user = {
      id: 1,
      nombre: 'Ada Admin',
      rol: 'admin',
      is_active: true,
      asignaciones_territoriales: [],
    };

    const wrapper = mountDrawer({ user });

    expect(wrapper.text()).toContain('Sin asignaciones territoriales');
    expect(wrapper.find('[data-testid="org-drawer-territorial-list"]').exists()).toBe(false);
  });

  it('renderiza la lista completa de asignaciones territoriales con ámbito y responsabilidad', () => {
    const user = {
      id: 2,
      nombre: 'Tomás Técnico',
      rol: 'tecnico',
      is_active: true,
      asignaciones_territoriales: [
        {
          id: 101,
          ambito: 'piso',
          tipo_responsabilidad: 'tecnico',
          badge_texto: 'Encargado Piso 2 · Pabellón A',
          nombre_ambito: 'Pabellón A · Piso 2',
          piso: '2',
          activo: true,
        },
        {
          id: 102,
          ambito: 'edificio',
          tipo_responsabilidad: 'tecnico',
          badge_texto: 'Encargado Pabellón B',
          nombre_ambito: 'Pabellón B',
          activo: true,
        },
      ],
    };

    const wrapper = mountDrawer({ user });

    const list = wrapper.find('[data-testid="org-drawer-territorial-list"]');
    expect(list.exists()).toBe(true);
    expect(wrapper.text()).toContain('Encargado Piso 2 · Pabellón A');
    expect(wrapper.text()).toContain('Encargado Pabellón B');
    expect(wrapper.text()).toContain('Piso');
    expect(wrapper.text()).toContain('Pabellón');
    expect(wrapper.text()).toContain('Técnico');
    expect(wrapper.text()).toContain('Activo');
  });

  it('identifica y muestra supervisor auto-asociado por sede con badge distintivo', () => {
    const user = {
      id: 3,
      nombre: 'Tito Auto',
      rol: 'tecnico',
      is_active: true,
      supervisor_id: 2,
      supervisor_nombre: 'Carlos Responsable',
      supervisor_auto_asociado: true,
      supervisor: { id: 2, nombre_completo: 'Carlos Responsable', rol: 'responsable' },
      asignaciones_territoriales: [
        { id: 1, ambito: 'piso', badge_texto: 'Encargado Piso 1', tipo_responsabilidad: 'tecnico' },
      ],
    };

    const wrapper = mountDrawer({ user });

    expect(wrapper.text()).toContain('Carlos Responsable');
    expect(wrapper.text()).toContain('Auto-asociado por sede');
    expect(wrapper.find('svg.lucide-sparkles').exists()).toBe(true);
  });

  it('identifica y muestra supervisor formal con badge de jerarquía formal', () => {
    const user = {
      id: 4,
      nombre: 'Elena Formal',
      rol: 'responsable',
      is_active: true,
      supervisor_id: 1,
      supervisor_nombre: 'Ada Admin',
      supervisor_auto_asociado: false,
      supervisor: { id: 1, nombre_completo: 'Ada Admin', rol: 'admin' },
      asignaciones_territoriales: [],
    };

    const wrapper = mountDrawer({ user });

    expect(wrapper.text()).toContain('Ada Admin');
    expect(wrapper.text()).toContain('Jerarquía formal');
    expect(wrapper.find('svg.lucide-user-check').exists()).toBe(true);
  });

  it('muestra mensaje explicativo cuando el usuario no tiene supervisor directo', () => {
    const user = {
      id: 1,
      nombre: 'Ada Admin',
      rol: 'admin',
      is_active: true,
      supervisor_id: null,
      supervisor_nombre: null,
      supervisor: null,
    };

    const wrapper = mountDrawer({ user });

    expect(wrapper.text()).toContain('Sin supervisor directo asignado');
  });

  it('emite evento close al hacer clic en el botón de cerrar ficha', async () => {
    const user = { id: 5, nombre: 'Test', rol: 'tecnico' };
    const wrapper = mountDrawer({ user });

    const closeBtn = wrapper.find('button[aria-label="Cerrar ficha"]');
    expect(closeBtn.exists()).toBe(true);
    await closeBtn.trigger('click');

    expect(wrapper.emitted('close')).toBeTruthy();
  });

  it('aplica control de permisos en las acciones del pie de la ficha', () => {
    const targetUser = { id: 10, nombre: 'Operador', rol: 'tecnico' };

    // Usuario autenticado como técnico (solo lectura)
    const authTecnico = { id: 99, rol: 'tecnico', permissions: [] };
    const wrapperTecnico = mountDrawer({ user: targetUser }, authTecnico);

    expect(wrapperTecnico.text()).toContain('Cerrar ficha');
    expect(wrapperTecnico.text()).not.toContain('Editar datos');
    expect(wrapperTecnico.text()).not.toContain('Permisos CRUD');
    expect(wrapperTecnico.text()).not.toContain('Desactivar usuario');

    // Usuario autenticado como superadmin
    const authSuper = { id: 1, rol: 'superadmin', is_superuser: true, permissions: ['usuarios:editar', 'usuarios:eliminar'] };
    const wrapperSuper = mountDrawer({ user: targetUser }, authSuper);

    expect(wrapperSuper.text()).toContain('Editar datos');
    expect(wrapperSuper.text()).toContain('Permisos CRUD');
    expect(wrapperSuper.text()).toContain('Desactivar usuario');
  });
});
