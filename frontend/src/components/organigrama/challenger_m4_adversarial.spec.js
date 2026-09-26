import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, it } from 'vitest';

import OrgChartNode from '@/components/organigrama/OrgChartNode.vue';
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

describe('Adversarial Stress Test: OrgChartNode & OrgUserDrawer (Milestone 4)', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  // =========================================================================
  // SUITE 1: 0 Territorial Assignments (undefined, null, empty array, malformed)
  // =========================================================================
  describe('1. Zero Territorial Assignments & Defensive Null-Safety', () => {
    it('OrgChartNode: handles empty array without rendering badges or overflow counter', () => {
      const node = {
        id: 101,
        nombre: 'Sin Asignaciones',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [],
      };

      const wrapper = mount(OrgChartNode, { props: { node } });

      expect(wrapper.find('[data-testid="org-node-territorial-badges"]').exists()).toBe(false);
      expect(wrapper.findAll('[data-testid="territorial-badge"]')).toHaveLength(0);
      expect(wrapper.find('[data-testid="territorial-overflow"]').exists()).toBe(false);
    });

    it('OrgChartNode: survives null asignaciones_territoriales with zero DOM errors', () => {
      const node = {
        id: 102,
        nombre: 'Null Asignaciones',
        rol: 'docente',
        is_active: true,
        asignaciones_territoriales: null,
      };

      const wrapper = mount(OrgChartNode, { props: { node } });

      expect(wrapper.find('[data-testid="org-node-territorial-badges"]').exists()).toBe(false);
      expect(wrapper.findAll('[data-testid="territorial-badge"]')).toHaveLength(0);
      expect(wrapper.find('[data-testid="territorial-overflow"]').exists()).toBe(false);
    });

    it('OrgChartNode: survives undefined asignaciones_territoriales or missing key', () => {
      const node = {
        id: 103,
        nombre: 'Undefined Asignaciones',
        rol: 'admin',
        is_active: true,
      };

      const wrapper = mount(OrgChartNode, { props: { node } });

      expect(wrapper.find('[data-testid="org-node-territorial-badges"]').exists()).toBe(false);
      expect(wrapper.findAll('[data-testid="territorial-badge"]')).toHaveLength(0);
      expect(wrapper.find('[data-testid="territorial-overflow"]').exists()).toBe(false);
    });

    it('OrgChartNode: survives corrupted non-array types (string, boolean, number, object)', () => {
      const corruptNodes = [
        { id: 104, nombre: 'String Type', rol: 'tecnico', asignaciones_territoriales: 'not-an-array' },
        { id: 105, nombre: 'Number Type', rol: 'tecnico', asignaciones_territoriales: 12345 },
        { id: 106, nombre: 'Boolean Type', rol: 'tecnico', asignaciones_territoriales: true },
        { id: 107, nombre: 'Object Type', rol: 'tecnico', asignaciones_territoriales: { foo: 'bar' } },
      ];

      for (const node of corruptNodes) {
        expect(() => {
          const wrapper = mount(OrgChartNode, { props: { node } });
          expect(wrapper.find('[data-testid="org-node-territorial-badges"]').exists()).toBe(false);
          expect(wrapper.findAll('[data-testid="territorial-badge"]')).toHaveLength(0);
        }).not.toThrow();
      }
    });

    it('OrgUserDrawer: renders empty state text cleanly when user has 0 assignments', () => {
      const userEmpty = {
        id: 201,
        nombre: 'Cero Ámbitos',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [],
      };

      const wrapper = mountDrawer({ user: userEmpty });

      expect(wrapper.find('[data-testid="org-drawer-territorial-list"]').exists()).toBe(false);
      expect(wrapper.text()).toContain('Sin asignaciones territoriales asociadas a su cargo.');
    });

    it('OrgUserDrawer: renders empty state text cleanly when user asignaciones_territoriales is null/undefined', () => {
      const userNull = {
        id: 202,
        nombre: 'Null Ámbitos',
        rol: 'docente',
        is_active: true,
        asignaciones_territoriales: null,
      };

      const wrapper = mountDrawer({ user: userNull });

      expect(wrapper.find('[data-testid="org-drawer-territorial-list"]').exists()).toBe(false);
      expect(wrapper.text()).toContain('Sin asignaciones territoriales asociadas a su cargo.');
    });

    it('OrgUserDrawer: handles null user prop gracefully without throwing errors', () => {
      expect(() => {
        const wrapper = mountDrawer({ user: null });
        expect(wrapper.find('aside').exists()).toBe(false);
      }).not.toThrow();
    });
  });

  // =========================================================================
  // SUITE 2: Single Territorial Assignment (1 badge, no overflow, scope icons)
  // =========================================================================
  describe('2. Single Territorial Assignment Verification', () => {
    it('OrgChartNode: renders exactly 1 badge and NO overflow counter when 1 assignment present', () => {
      const node = {
        id: 301,
        nombre: 'Piso Tech',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [
          {
            id: 1,
            ambito: 'piso',
            badge_texto: 'Encargado Piso 2 · Pabellón A',
            tipo_responsabilidad: 'tecnico',
          },
        ],
      };

      const wrapper = mount(OrgChartNode, { props: { node } });

      const badges = wrapper.findAll('[data-testid="territorial-badge"]');
      expect(badges).toHaveLength(1);
      expect(badges[0].text()).toContain('Encargado Piso 2 · Pabellón A');
      expect(badges[0].classes()).toContain('bg-teal-50');
      expect(wrapper.find('svg.lucide-layers').exists()).toBe(true);

      // CRITICAL: Must not render overflow pill
      expect(wrapper.find('[data-testid="territorial-overflow"]').exists()).toBe(false);
    });

    it('OrgChartNode: verifies fallback to badge or nombre_ambito when badge_texto is absent', () => {
      const nodeWithBadge = {
        id: 302,
        nombre: 'Fallback User 1',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [{ ambito: 'edificio', badge: 'Pabellón Central' }],
      };
      const wrapper1 = mount(OrgChartNode, { props: { node: nodeWithBadge } });
      expect(wrapper1.find('[data-testid="territorial-badge"]').text()).toContain('Pabellón Central');

      const nodeWithNombreAmbito = {
        id: 303,
        nombre: 'Fallback User 2',
        rol: 'responsable',
        is_active: true,
        asignaciones_territoriales: [{ ambito: 'sede', nombre_ambito: 'Sede Norte' }],
      };
      const wrapper2 = mount(OrgChartNode, { props: { node: nodeWithNombreAmbito } });
      expect(wrapper2.find('[data-testid="territorial-badge"]').text()).toContain('Sede Norte');

      const nodeWithOnlyAmbito = {
        id: 304,
        nombre: 'Fallback User 3',
        rol: 'docente',
        is_active: true,
        asignaciones_territoriales: [{ ambito: 'espacio' }],
      };
      const wrapper3 = mount(OrgChartNode, { props: { node: nodeWithOnlyAmbito } });
      expect(wrapper3.find('[data-testid="territorial-badge"]').text()).toContain('espacio');
    });

    it('OrgChartNode: verifies correct formatting in formatTooltip for 1 assignment', () => {
      const node = {
        id: 305,
        nombre: 'Tooltip User',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [
          {
            ambito: 'piso',
            badge_texto: 'Encargado Piso 3 · Pabellón B',
            tipo_responsabilidad: 'tecnico',
          },
        ],
      };

      const wrapper = mount(OrgChartNode, { props: { node } });
      const badge = wrapper.find('[data-testid="territorial-badge"]');
      expect(badge.attributes('title')).toBe('Piso: Encargado Piso 3 · Pabellón B (tecnico)');
    });

    it('OrgUserDrawer: renders single assignment with responsibility pill and active state', () => {
      const user = {
        id: 306,
        nombre: 'Single Assign Drawer',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [
          {
            id: 88,
            ambito: 'espacio',
            badge_texto: 'LAB-102 · Edificio Sistemas',
            tipo_responsabilidad: 'tecnico',
            espacio_id: 102,
            piso: '1',
            activo: true,
          },
        ],
      };

      const wrapper = mountDrawer({ user });
      const list = wrapper.find('[data-testid="org-drawer-territorial-list"]');
      expect(list.exists()).toBe(true);
      expect(wrapper.text()).toContain('LAB-102 · Edificio Sistemas');
      expect(wrapper.text()).toContain('Espacio');
      expect(wrapper.text()).toContain('Técnico');
      expect(wrapper.text()).toContain('Activo');
      expect(wrapper.text()).toContain('Piso 1 · Espacio #102');
    });
  });

  // =========================================================================
  // SUITE 3: 5+ Assignments Across All Scopes, Overflow Counter & Layout Stress
  // =========================================================================
  describe('3. Multi-Scope (5+ Assignments), Overflow Counter & Layout Stability', () => {
    const multiAssignments = [
      { id: 1, ambito: 'sede', badge_texto: 'Responsable Campus Lima', tipo_responsabilidad: 'responsable' },
      { id: 2, ambito: 'edificio', badge_texto: 'Encargado Pabellón Central', tipo_responsabilidad: 'tecnico' },
      { id: 3, ambito: 'piso', badge_texto: 'Encargado Piso 1 · Pabellón A', tipo_responsabilidad: 'tecnico' },
      { id: 4, ambito: 'piso', badge_texto: 'Encargado Piso 2 · Pabellón A', tipo_responsabilidad: 'tecnico' },
      { id: 5, ambito: 'espacio', badge_texto: 'LAB-301 · Pabellón Central', tipo_responsabilidad: 'docente' },
      { id: 6, ambito: 'espacio', badge_texto: 'TALLER-10 · Campus Lima', tipo_responsabilidad: 'tecnico' },
    ];

    it('OrgChartNode: with default maxVisibleBadges (1), shows 1 badge and "+5 más" pill', () => {
      const node = {
        id: 401,
        nombre: 'Super Polymath',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: multiAssignments,
      };

      const wrapper = mount(OrgChartNode, {
        props: { node },
      });

      const badges = wrapper.findAll('[data-testid="territorial-badge"]');
      expect(badges).toHaveLength(1);
      expect(badges[0].text()).toContain('Responsable Campus Lima');

      const overflow = wrapper.find('[data-testid="territorial-overflow"]');
      expect(overflow.exists()).toBe(true);
      expect(overflow.text()).toBe('+5 más');

      const title = overflow.attributes('title');
      expect(title).toContain('Otros ámbitos a cargo:');
      expect(title).toContain('• Encargado Pabellón Central');
      expect(title).toContain('• Encargado Piso 1 · Pabellón A');
      expect(title).toContain('• Encargado Piso 2 · Pabellón A');
      expect(title).toContain('• LAB-301 · Pabellón Central');
      expect(title).toContain('• TALLER-10 · Campus Lima');
    });

    it('OrgChartNode: adjusts visible badges and remaining counter according to maxVisibleBadges prop', () => {
      const node = {
        id: 402,
        nombre: 'Multi Prop Tester',
        rol: 'responsable',
        is_active: true,
        asignaciones_territoriales: multiAssignments,
      };

      // Test with maxVisibleBadges = 2
      const wrapper2 = mount(OrgChartNode, {
        props: { node, maxVisibleBadges: 2 },
      });
      expect(wrapper2.findAll('[data-testid="territorial-badge"]')).toHaveLength(2);
      expect(wrapper2.find('[data-testid="territorial-overflow"]').text()).toBe('+4 más');

      // Test with maxVisibleBadges = 6 (all visible)
      const wrapper6 = mount(OrgChartNode, {
        props: { node, maxVisibleBadges: 6 },
      });
      expect(wrapper6.findAll('[data-testid="territorial-badge"]')).toHaveLength(6);
      expect(wrapper6.find('[data-testid="territorial-overflow"]').exists()).toBe(false);

      // Test with maxVisibleBadges = 10 (exceeds count)
      const wrapper10 = mount(OrgChartNode, {
        props: { node, maxVisibleBadges: 10 },
      });
      expect(wrapper10.findAll('[data-testid="territorial-badge"]')).toHaveLength(6);
      expect(wrapper10.find('[data-testid="territorial-overflow"]').exists()).toBe(false);
    });

    it('OrgChartNode: maintains compact card width and text truncation under extreme string length', () => {
      const extremeNode = {
        id: 403,
        nombre: 'Adversarial Long Strings User',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [
          {
            id: 99,
            ambito: 'piso',
            badge_texto: 'Encargado Piso 99999999 · Pabellón de Ciencias Experimentales Ultra Complejas de la Sede Principal Internacional',
            tipo_responsabilidad: 'tecnico',
          },
          {
            id: 100,
            ambito: 'espacio',
            badge_texto: 'Laboratorio de Nanotecnología Cuántica Avanzada y Computación Fotónica Espacial Sala A-999',
            tipo_responsabilidad: 'tecnico',
          },
        ],
      };

      const wrapper = mount(OrgChartNode, {
        props: { node: extremeNode, maxVisibleBadges: 1 },
      });

      // Assert outer card is strictly constrained to w-72
      const card = wrapper.find('.group.relative');
      expect(card.classes()).toContain('w-72');

      // Assert badge container uses truncate and max-w-[130px]
      const badgeTextSpan = wrapper.find('[data-testid="territorial-badge"] span.truncate');
      expect(badgeTextSpan.exists()).toBe(true);
      expect(badgeTextSpan.classes()).toContain('max-w-[130px]');
      expect(badgeTextSpan.classes()).toContain('truncate');

      // Assert overflow counter handles second item cleanly
      const overflow = wrapper.find('[data-testid="territorial-overflow"]');
      expect(overflow.text()).toBe('+1 más');
      expect(overflow.attributes('title')).toContain('Laboratorio de Nanotecnología Cuántica');
    });

    it('OrgChartNode: renders complete tree with root, branches and connector lines without distortion', () => {
      const treeNode = {
        id: 1,
        nombre: 'Root Manager',
        rol: 'admin',
        is_active: true,
        asignaciones_territoriales: multiAssignments,
        children: [
          {
            id: 2,
            nombre: 'Sub 1 (0 badges)',
            rol: 'tecnico',
            is_active: true,
            asignaciones_territoriales: [],
            children: [],
          },
          {
            id: 3,
            nombre: 'Sub 2 (1 badge)',
            rol: 'tecnico',
            is_active: true,
            asignaciones_territoriales: [multiAssignments[2]],
            children: [],
          },
          {
            id: 4,
            nombre: 'Sub 3 (5 badges)',
            rol: 'docente',
            is_active: true,
            asignaciones_territoriales: multiAssignments.slice(0, 5),
            children: [],
          },
        ],
      };

      const wrapper = mount(OrgChartNode, {
        props: { node: treeNode },
      });

      // Verify recursive rendering of children
      const childNodes = wrapper.findAllComponents(OrgChartNode);
      // Root renders 3 child instances recursively
      expect(childNodes).toHaveLength(3);

      // Verify connectors render between root and children
      const connectors = wrapper.findAll('.bg-slate-300');
      expect(connectors.length).toBeGreaterThan(0);
    });

    it('OrgUserDrawer: renders all 6 assignments across scopes with proper styling and headers', () => {
      const user = {
        id: 404,
        nombre: 'Multi Scope Drawer User',
        rol: 'responsable',
        is_active: true,
        asignaciones_territoriales: multiAssignments,
      };

      const wrapper = mountDrawer({ user });
      const items = wrapper.findAll('[data-testid="org-drawer-territorial-list"] > div');
      expect(items).toHaveLength(6);

      // Verify scope labels exist
      expect(wrapper.text()).toContain('Sede');
      expect(wrapper.text()).toContain('Pabellón');
      expect(wrapper.text()).toContain('Piso');
      expect(wrapper.text()).toContain('Espacio');

      // Verify counter badge in section header
      expect(wrapper.text()).toContain('6 ámbitos');
    });
  });

  // =========================================================================
  // SUITE 4: Supervisor States (Auto-associated vs Formal vs Null/Docente)
  // =========================================================================
  describe('4. Supervisor Edge Cases: Auto-associated vs Formal vs supervisor=null', () => {
    it('OrgUserDrawer: detects explicit supervisor_auto_asociado === true', () => {
      const user = {
        id: 501,
        nombre: 'Tecnico Auto Flagged',
        rol: 'tecnico',
        is_active: true,
        supervisor_id: 10,
        supervisor_nombre: 'Mariana Responsable',
        supervisor_auto_asociado: true,
        supervisor: { id: 10, nombre_completo: 'Mariana Responsable', rol: 'responsable' },
        asignaciones_territoriales: [{ ambito: 'piso', badge_texto: 'Encargado Piso 1', tipo_responsabilidad: 'tecnico' }],
      };

      const wrapper = mountDrawer({ user });

      expect(wrapper.text()).toContain('Auto-asociado por sede');
      expect(wrapper.text()).toContain('Mariana Responsable');

      // Check specific supervisor hierarchy badge
      const supBadge = wrapper.findAll('span').find((s) => s.text().includes('Auto-asociado por sede'));
      expect(supBadge.exists()).toBe(true);
      expect(supBadge.find('svg.lucide-sparkles').exists()).toBe(true);
      expect(supBadge.find('svg.lucide-user-check').exists()).toBe(false);
    });

    it('OrgUserDrawer: detects supervisor_origen === "auto"', () => {
      const user = {
        id: 502,
        nombre: 'Tecnico Origen Auto',
        rol: 'tecnico',
        is_active: true,
        supervisor_id: 10,
        supervisor_nombre: 'Mariana Responsable',
        supervisor_origen: 'auto',
        supervisor: { id: 10, nombre_completo: 'Mariana Responsable', rol: 'responsable' },
        asignaciones_territoriales: [{ ambito: 'piso', badge_texto: 'Encargado Piso 1' }],
      };

      const wrapper = mountDrawer({ user });

      expect(wrapper.text()).toContain('Auto-asociado por sede');
      expect(wrapper.find('svg.lucide-sparkles').exists()).toBe(true);
    });

    it('OrgUserDrawer: fallback heuristic detects tecnico with territorial assignment and responsable supervisor', () => {
      const user = {
        id: 503,
        nombre: 'Tecnico Heuristic Match',
        rol: 'tecnico',
        is_active: true,
        supervisor_id: 10,
        supervisor_nombre: 'Mariana Responsable',
        // Neither supervisor_auto_asociado nor supervisor_origen provided
        supervisor: { id: 10, nombre_completo: 'Mariana Responsable', rol: 'responsable' },
        asignaciones_territoriales: [{ ambito: 'piso', badge_texto: 'Encargado Piso 2' }],
      };

      const wrapper = mountDrawer({ user });

      expect(wrapper.text()).toContain('Auto-asociado por sede');
      expect(wrapper.find('svg.lucide-sparkles').exists()).toBe(true);
    });

    it('OrgUserDrawer: displays formal supervisor when supervisor_auto_asociado === false', () => {
      const user = {
        id: 504,
        nombre: 'Tecnico Formal Flagged',
        rol: 'tecnico',
        is_active: true,
        supervisor_id: 10,
        supervisor_nombre: 'Mariana Responsable',
        supervisor_auto_asociado: false,
        supervisor: { id: 10, nombre_completo: 'Mariana Responsable', rol: 'responsable' },
        asignaciones_territoriales: [{ ambito: 'piso', badge_texto: 'Encargado Piso 1' }],
      };

      const wrapper = mountDrawer({ user });

      expect(wrapper.text()).toContain('Jerarquía formal');
      expect(wrapper.text()).not.toContain('Auto-asociado por sede');
      expect(wrapper.find('svg.lucide-user-check').exists()).toBe(true);
      expect(wrapper.find('svg.lucide-sparkles').exists()).toBe(false);
    });

    it('OrgUserDrawer: non-tecnico (e.g. responsable) with admin supervisor shows formal hierarchy', () => {
      const user = {
        id: 505,
        nombre: 'Responsable User',
        rol: 'responsable',
        is_active: true,
        supervisor_id: 1,
        supervisor_nombre: 'Admin Boss',
        supervisor: { id: 1, nombre_completo: 'Admin Boss', rol: 'admin' },
        asignaciones_territoriales: [{ ambito: 'sede', badge_texto: 'Responsable Campus' }],
      };

      const wrapper = mountDrawer({ user });

      expect(wrapper.text()).toContain('Jerarquía formal');
      expect(wrapper.text()).not.toContain('Auto-asociado por sede');
      expect(wrapper.find('svg.lucide-user-check').exists()).toBe(true);
    });

    it('OrgUserDrawer: docente with supervisor=null displays empty supervisor notice while rendering territorial assignment', () => {
      const docenteUser = {
        id: 506,
        nombre: 'Profesor Carlos Docente',
        rol: 'docente',
        is_active: true,
        supervisor_id: null,
        supervisor_nombre: null,
        supervisor: null,
        asignaciones_territoriales: [
          {
            id: 201,
            ambito: 'espacio',
            badge_texto: 'LAB-105 · Pabellón B',
            tipo_responsabilidad: 'docente',
            espacio_id: 105,
            piso: '1',
            activo: true,
          },
        ],
      };

      const wrapper = mountDrawer({ user: docenteUser });

      // Supervisor direct state
      expect(wrapper.text()).toContain('Sin supervisor directo asignado (Nodo principal o de máxima autoridad).');
      expect(wrapper.text()).not.toContain('Auto-asociado por sede');
      expect(wrapper.text()).not.toContain('Jerarquía formal');
      expect(wrapper.find('svg.lucide-sparkles').exists()).toBe(false);
      expect(wrapper.find('svg.lucide-user-check').exists()).toBe(false);

      // Territorial assignment must render cleanly without interference
      expect(wrapper.find('[data-testid="org-drawer-territorial-list"]').exists()).toBe(true);
      expect(wrapper.text()).toContain('LAB-105 · Pabellón B');
      expect(wrapper.text()).toContain('Docente');
      expect(wrapper.text()).toContain('Espacio');
      expect(wrapper.find('svg.lucide-door-closed').exists()).toBe(true);
    });

    it('OrgUserDrawer: top-level superadmin with supervisor=null displays empty supervisor notice', () => {
      const topSuperadmin = {
        id: 1,
        nombre: 'Superadmin Supremo',
        rol: 'superadmin',
        is_active: true,
        supervisor_id: null,
        supervisor_nombre: null,
        supervisor: null,
        asignaciones_territoriales: [],
      };

      const wrapper = mountDrawer({ user: topSuperadmin });

      expect(wrapper.text()).toContain('Sin supervisor directo asignado (Nodo principal o de máxima autoridad).');
      expect(wrapper.text()).toContain('Sin asignaciones territoriales asociadas a su cargo.');
    });
  });

  // =========================================================================
  // SUITE 5: Boundary & Extreme Cases (Missing attributes, Inactive, Emits)
  // =========================================================================
  describe('5. Malformed Assignment Items and Status Inactivity Stress', () => {
    it('OrgChartNode: handles assignment item with missing properties without throwing', () => {
      const node = {
        id: 601,
        nombre: 'Malformed User',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [
          {}, // empty object
          { ambito: 'desconocido_scope' },
          { id: 99, badge_texto: '' },
        ],
      };

      expect(() => {
        const wrapper = mount(OrgChartNode, { props: { node } });
        const badges = wrapper.findAll('[data-testid="territorial-badge"]');
        expect(badges.length).toBeGreaterThan(0);
      }).not.toThrow();
    });

    it('OrgUserDrawer: correctly renders inactive territorial assignment badge', () => {
      const user = {
        id: 602,
        nombre: 'Inactive Assignee',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [
          {
            id: 77,
            ambito: 'piso',
            badge_texto: 'Encargado Piso 1 (Histórico)',
            tipo_responsabilidad: 'tecnico',
            activo: false,
          },
        ],
      };

      const wrapper = mountDrawer({ user });
      expect(wrapper.text()).toContain('Inactivo');
      expect(wrapper.find('.bg-slate-100.text-slate-500').exists()).toBe(true);
    });

    it('OrgChartNode: preserves reactivity and emits select when clicked with complex badges', async () => {
      const node = {
        id: 603,
        nombre: 'Interactive Node',
        rol: 'tecnico',
        is_active: true,
        asignaciones_territoriales: [
          { ambito: 'piso', badge_texto: 'Piso 1' },
          { ambito: 'piso', badge_texto: 'Piso 2' },
        ],
      };

      const wrapper = mount(OrgChartNode, { props: { node } });
      await wrapper.find('.group.relative').trigger('click');

      expect(wrapper.emitted('select')).toBeTruthy();
      expect(wrapper.emitted('select')[0][0].id).toBe(603);
    });
  });
});
