import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import CroquisPiso from '@/components/espacios/CroquisPiso.vue';
import OrgChartNode from '@/components/organigrama/OrgChartNode.vue';

describe('Tier 5 Cross-Module E2E User Journey (Milestone 5)', () => {
  describe('1. Organigrama Node Rendering', () => {
    it('renderiza al técnico con badge "Encargado Piso 2 · Pabellón A" y el icono Layers', () => {
      const node = {
        id: 10,
        nombre: 'Tomás',
        apellido: 'Técnico',
        nombre_completo: 'Tomás Técnico',
        username: 'ttecnico',
        rol: 'tecnico',
        is_active: true,
        supervisor_id: 5,
        supervisor_nombre: 'Roberto Responsable',
        sedes: [{ id: 1, nombre: 'Campus Central' }],
        asignaciones_territoriales: [
          {
            id: 101,
            ambito: 'piso',
            badge: 'Encargado Piso 2 · Pabellón A',
            badge_texto: 'Encargado Piso 2 · Pabellón A',
            tipo_responsabilidad: 'tecnico',
          },
        ],
        children: [],
      };

      const wrapper = mount(OrgChartNode, {
        props: { node },
      });

      // Validar presencia y contenido del badge territorial
      const badges = wrapper.findAll('[data-testid="territorial-badge"]');
      expect(badges).toHaveLength(1);
      expect(badges[0].text()).toContain('Encargado Piso 2 · Pabellón A');

      // Validar estilos teal y el icono oficial de Lucide Layers
      expect(badges[0].classes()).toContain('bg-teal-50');
      expect(badges[0].classes()).toContain('text-teal-700');
      const layersIcon = wrapper.find('svg.lucide-layers');
      expect(layersIcon.exists()).toBe(true);
    });
  });

  describe('2. CroquisPiso Contextual Header Chip & Precedence Over Spaces', () => {
    const mockFloor = {
      key: '2',
      piso: '2',
      label: 'Piso 2',
      edificio_id: 1,
      edificio_nombre: 'Pabellón A',
      local_id: 1,
      labs: 2,
      aulas: 0,
      spaces: [],
      encargado: {
        id: 101,
        usuario_id: 10,
        usuario_nombre: 'Tomás Técnico',
        tipo_responsabilidad: 'tecnico',
        badge_texto: 'Encargado Piso 2 · Pabellón A',
        activo: true,
      },
      allSpaces: [
        {
          id: 201,
          codigo_espacio: 'LAB-201',
          tipo: 'laboratorio',
          tipo_display: 'Laboratorio',
          cantidad_equipos: 15,
          resumen_equipos: {},
          // Tiene asignación directa (Diana Docente) Y heredada de piso (Tomás Técnico)
          encargados_directos: [
            { id: 301, usuario_nombre: 'Diana Docente', tipo_responsabilidad_display: 'Docente responsable' },
          ],
          encargados_heredados: [
            { id: 101, usuario_nombre: 'Tomás Técnico', origen: 'Piso 2 · Pabellón A' },
          ],
        },
        {
          id: 202,
          codigo_espacio: 'LAB-202',
          tipo: 'sala_computo',
          tipo_display: 'Sala de cómputo',
          cantidad_equipos: 20,
          resumen_equipos: {},
          // Solo tiene asignación heredada del piso
          encargados_directos: [],
          encargados_heredados: [
            { id: 101, usuario_nombre: 'Tomás Técnico', origen: 'Piso 2 · Pabellón A' },
          ],
        },
      ],
      layout: {
        filas: 2,
        columnas: 6,
        ambientes: [
          { espacio_id: 201, fila: 1, columna: 1, ancho: 2, alto: 2 },
          { espacio_id: 202, fila: 1, columna: 3, ancho: 2, alto: 2 },
        ],
        pasillos: [],
      },
    };

    it('CroquisPiso para Piso 2 visualiza al técnico en el chip de cabecera con icono UserRoundCheck', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: mockFloor, canEdit: true },
        global: {
          stubs: { RouterLink: { template: '<a><slot /></a>' } },
        },
      });

      const headerChip = wrapper.find('[data-testid="floor-technician-badge"]');
      expect(headerChip.exists()).toBe(true);
      expect(headerChip.text()).toContain('Tomás Técnico');
      expect(headerChip.text()).toContain('Encargado Piso 2 · Pabellón A');

      const userRoundCheck = headerChip.find('svg.lucide-user-round-check');
      expect(userRoundCheck.exists()).toBe(true);

      const changeBtn = wrapper.find('[data-testid="edit-floor-technician"]');
      expect(changeBtn.exists()).toBe(true);
    });

    it('los ambientes individuales sin asignación directa muestran el badge de técnico heredado con icono Layers', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: mockFloor },
        global: {
          stubs: { RouterLink: { template: '<a><slot /></a>' } },
        },
      });

      const articles = wrapper.findAll('article');
      const lab202 = articles.find((a) => a.text().includes('LAB-202'));
      expect(lab202).toBeDefined();

      const inheritedBadge = lab202.find('[data-testid="space-inherited-encargado"]');
      expect(inheritedBadge.exists()).toBe(true);
      expect(inheritedBadge.text()).toContain('Tomás Técnico');
      expect(inheritedBadge.text()).toContain('(Heredado)');

      const layersIcon = inheritedBadge.find('svg.lucide-layers');
      expect(layersIcon.exists()).toBe(true);
    });

    it('la asignación directa en un ambiente individual prevalece estrictamente sobre el badge heredado del piso', () => {
      const wrapper = mount(CroquisPiso, {
        props: { floor: mockFloor },
        global: {
          stubs: { RouterLink: { template: '<a><slot /></a>' } },
        },
      });

      const articles = wrapper.findAll('article');
      const lab201 = articles.find((a) => a.text().includes('LAB-201'));
      expect(lab201).toBeDefined();

      // Debe mostrar el badge directo de Diana Docente
      const directBadge = lab201.find('[data-testid="space-direct-encargado"]');
      expect(directBadge.exists()).toBe(true);
      expect(directBadge.text()).toContain('Diana Docente');
      const userCheckIcon = directBadge.find('svg.lucide-user-check');
      expect(userCheckIcon.exists()).toBe(true);

      // Precedencia estricta: NO debe renderizar el badge heredado en LAB-201
      const inheritedBadge = lab201.find('[data-testid="space-inherited-encargado"]');
      expect(inheritedBadge.exists()).toBe(false);
    });
  });
});
