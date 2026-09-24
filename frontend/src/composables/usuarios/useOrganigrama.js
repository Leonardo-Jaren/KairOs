import { computed, reactive, ref, shallowRef } from 'vue';

import permisosService from '@/services/permisos.service';
import usuariosService from '@/services/usuarios.service';
import { getApiErrorMessage } from '@/utils/api-errors';

const STORAGE_KEY = 'kairos_organigrama_view';

export function useOrganigrama(
  service = permisosService,
  userManagementService = usuariosService
) {
  const rawArbol = ref([]);
  const totalNodos = ref(0);
  const sedeInfo = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const assigningSupervisor = ref(false);
  const assigningUserId = ref(null);

  const selectedLocalId = ref('');
  const selectedUser = shallowRef(null);
  const drawerOpen = ref(false);

  const permisosModalOpen = ref(false);
  const permisosTargetUser = shallowRef(null);

  // Selector de vista persistente con localStorage
  const getStoredView = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved && ['mando', 'todos'].includes(saved)) {
        return saved;
      }
    } catch {
      // Ignorar fallo de lectura en navegacion privada
    }
    return 'mando';
  };

  const activeView = ref(getStoredView());

  const setActiveView = (view) => {
    if (['mando', 'todos'].includes(view)) {
      activeView.value = view;
      try {
        localStorage.setItem(STORAGE_KEY, view);
      } catch {
        // Ignorar fallo de escritura de almacenamiento
      }
    }
  };

  // Metadatos y conteos
  const meta = ref({
    total: 0,
    total_mando: 0,
    total_sin_supervisor: 0,
    total_docentes: 0,
    total_sin_sede: 0,
  });

  // Agrupaciones funcionales de nodos
  const grupos = ref({
    arbol_mando: [],
    sin_supervisor: [],
    docentes: [],
    sin_sede: [],
  });

  // Panel lateral de accion rapida (slide-over dock)
  const dockOpen = ref(false);
  const dockTab = ref('sin_supervisor'); // 'sin_supervisor' | 'docentes'

  const openDock = (tab = 'sin_supervisor') => {
    dockTab.value = tab;
    dockOpen.value = true;
  };

  const closeDock = () => {
    dockOpen.value = false;
  };

  const setDockTab = (tab) => {
    if (['sin_supervisor', 'docentes'].includes(tab)) {
      dockTab.value = tab;
    }
  };

  const toggleDock = (tab) => {
    if (tab && dockTab.value !== tab) {
      dockTab.value = tab;
      dockOpen.value = true;
    } else {
      dockOpen.value = !dockOpen.value;
    }
  };

  // Estado del lienzo: zoom y paneo
  const zoom = ref(1);
  const pan = reactive({ x: 0, y: 0 });
  const isDragging = ref(false);
  const hasDragged = ref(false);
  const dragStart = reactive({ x: 0, y: 0 });
  const dragStartPos = reactive({ x: 0, y: 0 });

  // Nodos colapsados en el arbol
  const collapsedNodes = ref(new Set());

  const isCollapsed = (nodeId) => collapsedNodes.value.has(nodeId);

  const toggleCollapse = (nodeId) => {
    const next = new Set(collapsedNodes.value);
    if (next.has(nodeId)) {
      next.delete(nodeId);
    } else {
      next.add(nodeId);
    }
    collapsedNodes.value = next;
  };

  const expandAll = () => {
    collapsedNodes.value = new Set();
  };

  const collapseAll = () => {
    const allIds = new Set();
    const collectIds = (nodes) => {
      for (const node of nodes) {
        if (node.children && node.children.length > 0) {
          allIds.add(node.id);
          collectIds(node.children);
        }
      }
    };
    collectIds(arbol.value);
    collapsedNodes.value = allIds;
  };

  // Controles de zoom
  const zoomIn = () => {
    zoom.value = Math.min(1.8, Number((zoom.value + 0.15).toFixed(2)));
  };

  const zoomOut = () => {
    zoom.value = Math.max(0.4, Number((zoom.value - 0.15).toFixed(2)));
  };

  const resetView = () => {
    zoom.value = 1;
    pan.x = 0;
    pan.y = 0;
  };

  // Eventos de arrastre para el lienzo
  const onMouseDown = (event) => {
    if (event.button !== 0) return;
    if (event.target.closest('button') || event.target.closest('input') || event.target.closest('select') || event.target.closest('a')) return;
    isDragging.value = true;
    hasDragged.value = false;
    dragStart.x = event.clientX - pan.x;
    dragStart.y = event.clientY - pan.y;
    dragStartPos.x = event.clientX;
    dragStartPos.y = event.clientY;
  };

  const onMouseMove = (event) => {
    if (!isDragging.value) return;
    const dx = Math.abs(event.clientX - dragStartPos.x);
    const dy = Math.abs(event.clientY - dragStartPos.y);
    if (dx > 4 || dy > 4) {
      hasDragged.value = true;
    }
    pan.x = event.clientX - dragStart.x;
    pan.y = event.clientY - dragStart.y;
  };

  const onMouseUp = () => {
    isDragging.value = false;
    setTimeout(() => {
      hasDragged.value = false;
    }, 50);
  };

  // Eventos de arrastre tactil para dispositivos moviles y pantallas tactiles
  const onTouchStart = (event) => {
    if (!event.touches || event.touches.length !== 1) return;
    const touch = event.touches[0];
    if (event.target?.closest?.('button') || event.target?.closest?.('input') || event.target?.closest?.('select') || event.target?.closest?.('a')) return;
    isDragging.value = true;
    hasDragged.value = false;
    dragStart.x = touch.clientX - pan.x;
    dragStart.y = touch.clientY - pan.y;
    dragStartPos.x = touch.clientX;
    dragStartPos.y = touch.clientY;
  };

  const onTouchMove = (event) => {
    if (!isDragging.value || !event.touches || event.touches.length !== 1) return;
    const touch = event.touches[0];
    const dx = Math.abs(touch.clientX - dragStartPos.x);
    const dy = Math.abs(touch.clientY - dragStartPos.y);
    if (dx > 4 || dy > 4) {
      hasDragged.value = true;
    }
    pan.x = touch.clientX - dragStart.x;
    pan.y = touch.clientY - dragStart.y;
  };

  const onTouchEnd = () => {
    isDragging.value = false;
    setTimeout(() => {
      hasDragged.value = false;
    }, 50);
  };

  // Paneo y zoom con la rueda del raton
  const onWheel = (event) => {
    if (event.ctrlKey || event.metaKey) {
      if (event.deltaY < 0) {
        zoomIn();
      } else {
        zoomOut();
      }
    } else {
      pan.x -= event.deltaX;
      pan.y -= event.deltaY;
    }
  };

  // Calculo reactivo auxiliar de grupos y metadatos cuando el backend retorna formato base
  const computeGruposAndMeta = (nodes) => {
    const flatten = (items) => {
      const flat = [];
      for (const item of items) {
        flat.push(item);
        if (item.children && item.children.length > 0) {
          flat.push(...flatten(item.children));
        }
      }
      return flat;
    };

    const allFlat = flatten(nodes);
    let mando = nodes.filter(
      (n) => (n.children && n.children.length > 0) || n.rol === 'superadmin'
    );
    if (mando.length === 0 && nodes.length > 0) {
      mando = nodes.filter((n) => ['superadmin', 'admin'].includes(n.rol));
    }
    if (mando.length === 0 && nodes.length > 0) {
      mando = nodes.filter((n) => n.rol === 'responsable');
    }
    const mandoIds = new Set(mando.map((n) => n.id));
    const docentes = nodes.filter((n) => n.rol === 'docente');
    const sinSupervisor = nodes.filter(
      (n) => n.rol !== 'docente' && !mandoIds.has(n.id)
    );
    const sinSede = allFlat.filter((n) => !n.sedes || n.sedes.length === 0);

    const countDescendants = (n) =>
      (n.children || []).reduce((acc, c) => acc + 1 + countDescendants(c), 0);

    grupos.value = {
      arbol_mando: mando,
      sin_supervisor: sinSupervisor,
      docentes,
      sin_sede: sinSede,
    };

    meta.value = {
      total: allFlat.length,
      total_mando: mando.reduce((acc, n) => acc + 1 + countDescendants(n), 0),
      total_sin_supervisor: sinSupervisor.length,
      total_docentes: docentes.length,
      total_sin_sede: sinSede.length,
    };
  };

  // Arbol filtrado segun el modo de vista activo (mando o panoramico completo)
  const displayArbol = computed(() => {
    if (activeView.value === 'todos') {
      return rawArbol.value;
    }
    return grupos.value.arbol_mando && grupos.value.arbol_mando.length > 0
      ? grupos.value.arbol_mando
      : rawArbol.value;
  });

  const arbol = computed({
    get() {
      return displayArbol.value;
    },
    set(newVal) {
      rawArbol.value = newVal || [];
      computeGruposAndMeta(rawArbol.value);
    },
  });

  // Carga de datos del organigrama
  const loadOrganigrama = async () => {
    loading.value = true;
    error.value = null;
    try {
      const params = {};
      if (selectedLocalId.value) {
        params.local_id = selectedLocalId.value;
      }
      const data = await service.obtenerOrganigrama(params);
      rawArbol.value = data.arbol || [];

      if (data.grupos && data.meta) {
        grupos.value = data.grupos;
        meta.value = data.meta;
      } else {
        computeGruposAndMeta(rawArbol.value);
      }

      totalNodos.value = data.total_nodos || meta.value.total;
      sedeInfo.value = data.sede || null;
    } catch (err) {
      error.value = getApiErrorMessage(err, 'No se pudo cargar el organigrama.');
    } finally {
      loading.value = false;
    }
  };

  // Busqueda recursiva de nodo por ID en el arbol jerarquico
  const findNodeById = (nodeId, nodes = rawArbol.value) => {
    if (!nodeId || !Array.isArray(nodes)) return null;
    for (const node of nodes) {
      if (node.id === nodeId) return node;
      if (Array.isArray(node.children) && node.children.length > 0) {
        const found = findNodeById(nodeId, node.children);
        if (found) return found;
      }
    }
    return null;
  };

  // Extractor seguro de asignaciones territoriales
  const getTerritorialBadges = (node) => {
    return Array.isArray(node?.asignaciones_territoriales) ? node.asignaciones_territoriales : [];
  };

  // Verificador de existencia de asignaciones territoriales
  const hasTerritorialAssignments = (node) => {
    return getTerritorialBadges(node).length > 0;
  };

  // Asignacion reactiva de supervisor directo
  const assignSupervisor = async (usuarioId, supervisorId) => {
    if (!usuarioId || !supervisorId) return false;
    assigningSupervisor.value = true;
    assigningUserId.value = usuarioId;
    error.value = null;
    try {
      await userManagementService.actualizar(usuarioId, { supervisor_id: supervisorId });
      await loadOrganigrama();
      // Resincronizar usuario activo en drawer si coincide
      if (selectedUser.value && selectedUser.value.id === usuarioId) {
        const refreshed = findNodeById(usuarioId);
        if (refreshed) {
          selectedUser.value = refreshed;
        }
      }
      return true;
    } catch (err) {
      error.value = getApiErrorMessage(err, 'No se pudo asignar el supervisor.');
      throw err;
    } finally {
      assigningSupervisor.value = false;
      assigningUserId.value = null;
    }
  };

  // Manejo de la ficha modal del usuario
  const openDrawer = (user) => {
    selectedUser.value = user;
    drawerOpen.value = true;
  };

  const closeDrawer = () => {
    drawerOpen.value = false;
    selectedUser.value = null;
  };

  // Manejo de la Matriz de Permisos Modal
  const openPermisos = (user) => {
    permisosTargetUser.value = user;
    permisosModalOpen.value = true;
  };

  const closePermisos = () => {
    permisosModalOpen.value = false;
    permisosTargetUser.value = null;
  };

  return {
    rawArbol,
    arbol,
    displayArbol,
    totalNodos,
    sedeInfo,
    loading,
    error,
    assigningSupervisor,
    assigningUserId,
    selectedLocalId,
    selectedUser,
    drawerOpen,
    permisosModalOpen,
    permisosTargetUser,
    activeView,
    setActiveView,
    meta,
    grupos,
    dockOpen,
    dockTab,
    openDock,
    closeDock,
    setDockTab,
    toggleDock,
    assignSupervisor,
    findNodeById,
    getTerritorialBadges,
    hasTerritorialAssignments,
    zoom,
    pan,
    isDragging,
    hasDragged,
    collapsedNodes,
    isCollapsed,
    toggleCollapse,
    expandAll,
    collapseAll,
    zoomIn,
    zoomOut,
    resetView,
    onMouseDown,
    onMouseMove,
    onMouseUp,
    onTouchStart,
    onTouchMove,
    onTouchEnd,
    onWheel,
    loadOrganigrama,
    openDrawer,
    closeDrawer,
    openPermisos,
    closePermisos,
  };
}
