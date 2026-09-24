import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useOrganigrama } from '@/composables/usuarios/useOrganigrama';

const mockOrganigramaConBadges = {
  sede: { id: 1, codigo: 'LOC-01', nombre: 'Campus Central Huánuco', ciudad: 'Huánuco' },
  total_nodos: 3,
  arbol: [
    {
      id: 1,
      nombre: 'Ada Admin',
      rol: 'admin',
      is_active: true,
      asignaciones_territoriales: [],
      subordinados_count: 1,
      children: [
        {
          id: 2,
          nombre: 'Carlos Encargado',
          rol: 'responsable',
          is_active: true,
          asignaciones_territoriales: [
            {
              id: 1,
              ambito: 'sede',
              tipo_responsabilidad: 'responsable',
              badge_texto: 'Responsable · Campus Central',
            },
          ],
          subordinados_count: 1,
          children: [
            {
              id: 3,
              nombre: 'Tomás Técnico',
              rol: 'tecnico',
              is_active: true,
              asignaciones_territoriales: [
                {
                  id: 2,
                  ambito: 'piso',
                  tipo_responsabilidad: 'tecnico',
                  badge_texto: 'Encargado Piso 2 · Pabellón A',
                },
              ],
              children: [],
            },
          ],
        },
      ],
    },
  ],
};

const createMockService = (data = mockOrganigramaConBadges) => ({
  obtenerOrganigrama: vi.fn().mockResolvedValue(data),
});

describe('E2E Frontend: useOrganigrama (Features 8, 13)', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('Feature 8 & 13: procesa e ingesta asignaciones territoriales en los nodos del árbol', async () => {
    const service = createMockService();
    const composable = useOrganigrama(service);

    await composable.loadOrganigrama();

    expect(composable.arbol.value).toHaveLength(1);
    const responsable = composable.arbol.value[0].children[0];
    expect(responsable.nombre).toBe('Carlos Encargado');
    expect(responsable.asignaciones_territoriales).toHaveLength(1);
    expect(responsable.asignaciones_territoriales[0].badge_texto).toBe('Responsable · Campus Central');

    const tecnico = responsable.children[0];
    expect(tecnico.nombre).toBe('Tomás Técnico');
    expect(tecnico.asignaciones_territoriales).toHaveLength(1);
    expect(tecnico.asignaciones_territoriales[0].badge_texto).toBe('Encargado Piso 2 · Pabellón A');
  });

  it('Feature 13: permite abrir drawer lateral inspeccionando datos y badges del usuario seleccionado', async () => {
    const composable = useOrganigrama(createMockService());
    await composable.loadOrganigrama();

    const tecnico = composable.arbol.value[0].children[0].children[0];
    composable.openDrawer(tecnico);

    expect(composable.drawerOpen.value).toBe(true);
    expect(composable.selectedUser.value?.id).toBe(3);
    expect(composable.selectedUser.value?.asignaciones_territoriales[0].badge_texto).toBe(
      'Encargado Piso 2 · Pabellón A'
    );
  });
});
