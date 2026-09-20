import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useOrganigrama } from '@/composables/usuarios/useOrganigrama';

const mockOrganigramaData = {
  sede: { id: 1, codigo: 'LOC-01', nombre: 'Huánuco Central', ciudad: 'Huánuco' },
  total_nodos: 3,
  arbol: [
    {
      id: 1,
      nombre: 'Ada Admin',
      rol: 'admin',
      is_active: true,
      subordinados_count: 2,
      children: [
        {
          id: 2,
          nombre: 'Carlos Encargado',
          rol: 'responsable',
          is_active: true,
          subordinados_count: 1,
          children: [
            {
              id: 3,
              nombre: 'Tito Tecnico',
              rol: 'tecnico',
              is_active: true,
              children: [],
            },
          ],
        },
      ],
    },
  ],
};

const mockOrganigramaExtendedData = {
  sede: { id: 1, codigo: 'LOC-01', nombre: 'Campus Central', ciudad: 'Huánuco' },
  total_nodos: 4,
  arbol: [
    {
      id: 1,
      nombre: 'Ada Admin',
      rol: 'admin',
      is_active: true,
      children: [
        { id: 2, nombre: 'Tito Tecnico', rol: 'tecnico', is_active: true, children: [] },
      ],
    },
    { id: 3, nombre: 'Daniel Docente', rol: 'docente', is_active: true, children: [] },
    { id: 4, nombre: 'Hugo Huerfano', rol: 'usuario', is_active: true, children: [] },
  ],
  meta: {
    total: 4,
    total_mando: 2,
    total_sin_supervisor: 1,
    total_docentes: 1,
    total_sin_sede: 0,
  },
  grupos: {
    arbol_mando: [
      {
        id: 1,
        nombre: 'Ada Admin',
        rol: 'admin',
        is_active: true,
        children: [{ id: 2, nombre: 'Tito Tecnico', rol: 'tecnico', is_active: true, children: [] }],
      },
    ],
    sin_supervisor: [{ id: 4, nombre: 'Hugo Huerfano', rol: 'usuario', is_active: true, children: [] }],
    docentes: [{ id: 3, nombre: 'Daniel Docente', rol: 'docente', is_active: true, children: [] }],
    sin_sede: [],
  },
};

const createMockService = (data = mockOrganigramaData) => ({
  obtenerOrganigrama: vi.fn().mockResolvedValue(data),
});

const createMockUserService = () => ({
  actualizar: vi.fn().mockResolvedValue({ id: 4, supervisor_id: 1 }),
});

describe('useOrganigrama', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('carga la jerarquía de árbol y metadatos de sede', async () => {
    const service = createMockService();
    const composable = useOrganigrama(service);

    await composable.loadOrganigrama();

    expect(service.obtenerOrganigrama).toHaveBeenCalledWith({});
    expect(composable.arbol.value).toHaveLength(1);
    expect(composable.totalNodos.value).toBe(3);
    expect(composable.sedeInfo.value?.codigo).toBe('LOC-01');
  });

  it('permite filtrar el organigrama por sede seleccionada', async () => {
    const service = createMockService();
    const composable = useOrganigrama(service);
    composable.selectedLocalId.value = 1;

    await composable.loadOrganigrama();

    expect(service.obtenerOrganigrama).toHaveBeenCalledWith({ local_id: 1 });
  });

  it('gestiona zoom in, zoom out y resetView correctamente dentro de límites', () => {
    const composable = useOrganigrama(createMockService());

    expect(composable.zoom.value).toBe(1);
    composable.zoomIn();
    expect(composable.zoom.value).toBe(1.15);

    composable.zoomOut();
    composable.zoomOut();
    expect(composable.zoom.value).toBe(0.85);

    composable.resetView();
    expect(composable.zoom.value).toBe(1);
    expect(composable.pan.x).toBe(0);
    expect(composable.pan.y).toBe(0);
  });

  it('colapsa y expande ramas individuales y masivamente', () => {
    const composable = useOrganigrama(createMockService());
    composable.arbol.value = mockOrganigramaData.arbol;

    expect(composable.isCollapsed(1)).toBe(false);
    composable.toggleCollapse(1);
    expect(composable.isCollapsed(1)).toBe(true);

    composable.toggleCollapse(1);
    expect(composable.isCollapsed(1)).toBe(false);

    composable.collapseAll();
    expect(composable.isCollapsed(1)).toBe(true);
    expect(composable.isCollapsed(2)).toBe(true);

    composable.expandAll();
    expect(composable.isCollapsed(1)).toBe(false);
    expect(composable.isCollapsed(2)).toBe(false);
  });

  it('abre y cierra el drawer lateral y el modal de permisos', () => {
    const composable = useOrganigrama(createMockService());
    const user = mockOrganigramaData.arbol[0];

    composable.openDrawer(user);
    expect(composable.drawerOpen.value).toBe(true);
    expect(composable.selectedUser.value?.id).toBe(1);

    composable.closeDrawer();
    expect(composable.drawerOpen.value).toBe(false);
    expect(composable.selectedUser.value).toBeNull();

    composable.openPermisos(user);
    expect(composable.permisosModalOpen.value).toBe(true);
    expect(composable.permisosTargetUser.value?.id).toBe(1);

    composable.closePermisos();
    expect(composable.permisosModalOpen.value).toBe(false);
    expect(composable.permisosTargetUser.value).toBeNull();
  });

  it('procesa meta y grupos aditivos y conmuta entre modo mando y todos', async () => {
    const service = createMockService(mockOrganigramaExtendedData);
    const composable = useOrganigrama(service);

    await composable.loadOrganigrama();

    expect(composable.meta.value.total_sin_supervisor).toBe(1);
    expect(composable.meta.value.total_docentes).toBe(1);
    expect(composable.grupos.value.sin_supervisor).toHaveLength(1);

    // Por defecto modo mando muestra solo arbol_mando
    expect(composable.activeView.value).toBe('mando');
    expect(composable.displayArbol.value).toHaveLength(1);
    expect(composable.displayArbol.value[0].id).toBe(1);

    // Conmutar a vista todos
    composable.setActiveView('todos');
    expect(composable.activeView.value).toBe('todos');
    expect(composable.displayArbol.value).toHaveLength(3);
    expect(localStorage.getItem('kairos_organigrama_view')).toBe('todos');
  });

  it('gestiona la apertura y cambio de pestana del dock lateral', () => {
    const composable = useOrganigrama(createMockService());

    expect(composable.dockOpen.value).toBe(false);
    expect(composable.dockTab.value).toBe('sin_supervisor');

    composable.openDock('docentes');
    expect(composable.dockOpen.value).toBe(true);
    expect(composable.dockTab.value).toBe('docentes');

    composable.toggleDock('sin_supervisor');
    expect(composable.dockOpen.value).toBe(true);
    expect(composable.dockTab.value).toBe('sin_supervisor');

    composable.closeDock();
    expect(composable.dockOpen.value).toBe(false);
  });

  it('asigna supervisor llamando al servicio y recargando datos', async () => {
    const service = createMockService(mockOrganigramaExtendedData);
    const userService = createMockUserService();
    const composable = useOrganigrama(service, userService);

    await composable.loadOrganigrama();
    expect(composable.assigningUserId.value).toBeNull();

    const result = await composable.assignSupervisor(4, 1);

    expect(result).toBe(true);
    expect(composable.assigningUserId.value).toBeNull();
    expect(userService.actualizar).toHaveBeenCalledWith(4, { supervisor_id: 1 });
    expect(service.obtenerOrganigrama).toHaveBeenCalledTimes(2);
  });

  it('inicializa activeView desde localStorage si existe valor guardado', () => {
    localStorage.setItem('kairos_organigrama_view', 'todos');
    const composable = useOrganigrama(createMockService());
    expect(composable.activeView.value).toBe('todos');
  });

  it('permite cambiar dockTab directamente con setDockTab', () => {
    const composable = useOrganigrama(createMockService());
    expect(composable.dockTab.value).toBe('sin_supervisor');

    composable.setDockTab('docentes');
    expect(composable.dockTab.value).toBe('docentes');

    composable.setDockTab('sin_supervisor');
    expect(composable.dockTab.value).toBe('sin_supervisor');

    // Ignora tabs invalidos
    composable.setDockTab('invalido');
    expect(composable.dockTab.value).toBe('sin_supervisor');
  });

  it('gestiona arrastre interactivo por raton y por eventos tactiles (touch)', () => {
    const composable = useOrganigrama(createMockService());

    // Arrastre con raton
    expect(composable.isDragging.value).toBe(false);
    composable.onMouseDown({ button: 0, clientX: 100, clientY: 150, target: document.createElement('div') });
    expect(composable.isDragging.value).toBe(true);

    composable.onMouseMove({ clientX: 120, clientY: 180 });
    expect(composable.pan.x).toBe(20);
    expect(composable.pan.y).toBe(30);

    composable.onMouseUp();
    expect(composable.isDragging.value).toBe(false);

    // Arrastre con eventos touch
    composable.onTouchStart({
      touches: [{ clientX: 200, clientY: 200 }],
      target: document.createElement('div'),
    });
    expect(composable.isDragging.value).toBe(true);

    composable.onTouchMove({
      touches: [{ clientX: 250, clientY: 230 }],
    });
    expect(composable.pan.x).toBe(70);
    expect(composable.pan.y).toBe(60);

    composable.onTouchEnd();
    expect(composable.isDragging.value).toBe(false);
  });
});
