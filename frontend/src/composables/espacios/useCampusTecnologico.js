import { computed, onMounted, reactive, ref, watch } from 'vue';

import edificiosService from '@/services/edificios.service';
import espaciosService from '@/services/espacios.service';
import espaciosUsuariosService from '@/services/espacios-usuarios.service';
import localesService from '@/services/locales.service';
import { listarTodas, useCampusTerritorio } from '@/composables/espacios/useCampusTerritorio';
import { useLocalesCampus } from '@/composables/espacios/useLocalesCampus';
export { listarTodas } from '@/composables/espacios/useCampusTerritorio';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';
import { formatFloor } from '@/utils/formatters';
import { normalizeFloorLayout, useCroquisPiso } from '@/composables/espacios/useCroquisPiso';

const naturalCompare = (left, right) => String(left).localeCompare(String(right), 'es', {
  numeric: true,
  sensitivity: 'base',
});
const normalizeFloorValue = (value) => String(value ?? '')
  .trim()
  .replace(/^piso\s*/i, '')
  .trim();

export const formatCountLabel = (count, singular, plural) => (
  count === 1 ? singular : plural
);

const emptyBuilding = () => ({ codigo: '', nombre: '', descripcion: '', local_id: '', activo: true });
const emptySpace = () => ({
  codigo_espacio: '',
  tipo: 'laboratorio',
  edificio_id: '',
  piso: '',
  activo: true,
});

export function useCampusTecnologico(
  spaceService = espaciosService,
  buildingService = edificiosService,
  localService = localesService,
  navigation = {},
  asignacionesService = espaciosUsuariosService,
) {
  const authStore = useAuthStore();
  const spaces = ref([]);
  const buildingRecords = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const error = ref('');
  const search = ref('');
  const localRecords = ref([]);
  const activeFloorKey = ref(normalizeFloorValue(navigation.route?.query?.piso) || '');
  const buildingModalOpen = ref(false);
  const buildingDeleteOpen = ref(false);
  const editingBuilding = ref(null);
  const pendingBuildingDelete = ref(null);
  const buildingForm = reactive(emptyBuilding());
  const buildingErrors = reactive({});
  const spaceModalOpen = ref(false);
  const spaceDeleteOpen = ref(false);
  const editingSpace = ref(null);
  const pendingSpaceDelete = ref(null);
  const spaceForm = reactive(emptySpace());
  const spaceErrors = reactive({});
  const toast = reactive({ show: false, message: '', type: 'success' });
  const showToast = (message, type = 'success') => Object.assign(toast, { show: true, message, type });

  const floorAssignments = ref([]);
  const technicianModalOpen = ref(false);
  const technicianSaving = ref(false);
  const technicianLoading = ref(false);
  const technicianTarget = ref(null);
  const technicianOptions = ref([]);
  const technicianForm = reactive({
    assignment_id: null,
    usuario_id: '',
    tipo_responsabilidad: 'tecnico',
  });

  const canEdit = computed(() => (
    authStore.isSuperAdmin
    || authStore.isAdmin
    || authStore.hasPermission('espacios', 'editar')
  ));
  const isEditingBuilding = computed(() => Boolean(editingBuilding.value));
  const isEditingSpace = computed(() => Boolean(editingSpace.value));
  const typeOptions = [
    { value: 'laboratorio', label: 'Laboratorio' },
    { value: 'sala_computo', label: 'Sala de cómputo' },
    { value: 'aula', label: 'Aula' },
    { value: 'oficina', label: 'Oficina' },
    { value: 'otro', label: 'Otro' },
  ];

  const territorio = useCampusTerritorio({
    buildingRecords, localRecords, navigation,
    isEditing: () => Boolean(editingFloor.value) || floorSaving.value,
    showToast,
  });
  const { selectedBuildingId, currentBuildingRecords, refreshSelection,
    selectionBlocked, selectSavedBuilding } = territorio;
  const currentSpaces = computed(() => {
    const ids = new Set(currentBuildingRecords.value.map((building) => Number(building.id)));
    return spaces.value.filter((space) => ids.has(Number(space.edificio_id ?? space.edificio?.id)));
  });

  const edificios = computed(() => currentBuildingRecords.value.map((building) => {
    const buildingSpaces = currentSpaces.value.filter((space) => (
      Number(space.edificio_id ?? space.edificio?.id) === Number(building.id)
    ));
    const floors = [...new Set(buildingSpaces.map((space) => normalizeFloorValue(space.piso)))].sort(naturalCompare);
    return {
      ...building,
      spaces: buildingSpaces,
      pisos: floors,
      laboratorios: buildingSpaces.filter((space) => ['laboratorio', 'sala_computo'].includes(space.tipo)),
      aulas: buildingSpaces.filter((space) => space.tipo === 'aula'),
      equipos: buildingSpaces.reduce((total, space) => total + Number(space.cantidad_equipos ?? 0), 0),
      alertas: buildingSpaces.reduce((total, space) => (
        total + (space.resumen_equipos?.en_mantenimiento ?? 0) + (space.resumen_equipos?.dañado ?? 0)
      ), 0),
    };
  }));
  const buildingColumnCount = computed(() => Math.min(3, Math.max(1, edificios.value.length)));

  const edificioActivo = computed(() => (
    edificios.value.find((building) => String(building.id) === String(selectedBuildingId.value))
    ?? null
  ));

  const {
    editingFloor, floorDraft, floorTool, selectedFloorSpaceId, floorSaving,
    startFloorEditing, cancelFloorEditing, selectFloorSpace, setFloorTool,
    handleFloorCell, resizeSelectedFloorSpace, updateFloorColumns, addFloorRow,
    removeFloorRow, saveFloorLayout,
  } = useCroquisPiso({
    buildingRecords,
    activeBuilding: edificioActivo,
    buildingService,
    showToast,
  });

  const loadFloorAssignments = async (buildingId) => {
    if (!buildingId) {
      floorAssignments.value = [];
      return;
    }
    try {
      const res = await asignacionesService.listar({
        ambito: 'piso',
        edificio_id: buildingId,
        activo: 'true',
        page_size: 100,
      });
      floorAssignments.value = res.results ?? res ?? [];
    } catch {
      floorAssignments.value = [];
    }
  };

  watch(selectedBuildingId, (newId) => {
    if (newId) loadFloorAssignments(newId);
    else floorAssignments.value = [];
  }, { immediate: true });

  const getFloorEncargado = (floor) => {
    const normalized = normalizeFloorValue(floor);
    const match = floorAssignments.value.find((asig) => (
      normalizeFloorValue(asig.piso) === normalized
      && asig.activo !== false
    ));
    if (!match) return null;
    return {
      id: match.id,
      usuario_id: match.usuario?.id ?? match.usuario_id,
      usuario_nombre: match.usuario?.nombre_completo ?? `${match.usuario?.nombre ?? ''} ${match.usuario?.apellido ?? ''}`.trim(),
      correo: match.usuario?.correo ?? '',
      tipo_responsabilidad: match.tipo_responsabilidad ?? 'tecnico',
      tipo_responsabilidad_display: match.tipo_responsabilidad_display ?? 'Técnico',
      badge_texto: match.badge_texto ?? `Encargado Piso ${match.piso}`,
      activo: match.activo,
    };
  };

  const pisosVisibles = computed(() => {
    const query = search.value.trim().toLocaleLowerCase('es');
    const filtered = (edificioActivo.value?.spaces ?? []).filter((space) => (
      !query || [
        space.codigo_espacio,
        space.tipo_display,
        space.piso,
        space.responsable?.nombre_completo,
      ].some((value) => String(value ?? '').toLocaleLowerCase('es').includes(query))
    ));
    const groups = new Map();
    (edificioActivo.value?.spaces ?? []).forEach((space) => {
      const floor = normalizeFloorValue(space.piso);
      if (!groups.has(floor)) groups.set(floor, []);
      groups.get(floor).push(space);
    });
    return [...groups.entries()]
      .sort(([left], [right]) => naturalCompare(left, right))
      .map(([floor, allFloorSpaces]) => {
        const sortedSpaces = allFloorSpaces.sort((left, right) => naturalCompare(left.codigo_espacio, right.codigo_espacio));
        const visibleSpaces = sortedSpaces.filter((space) => filtered.includes(space));
        const storedFloors = edificioActivo.value?.configuracion_croquis?.pisos ?? {};
        const storedLayout = storedFloors[floor] ?? Object.entries(storedFloors)
          .find(([key]) => normalizeFloorValue(key) === floor)?.[1];
        return {
          key: floor,
          piso: floor,
          label: formatFloor(floor),
          edificio_id: Number(edificioActivo.value?.id ?? allFloorSpaces[0]?.edificio_id ?? allFloorSpaces[0]?.edificio?.id ?? 0) || null,
          edificio_nombre: edificioActivo.value?.nombre ?? allFloorSpaces[0]?.edificio?.nombre ?? allFloorSpaces[0]?.pabellon ?? '',
          local_id: Number(edificioActivo.value?.local_id ?? edificioActivo.value?.local?.id ?? territorio.selectedLocalId.value ?? allFloorSpaces[0]?.local_id ?? 0) || null,
          encargado: getFloorEncargado(floor),
          spaces: visibleSpaces,
          allSpaces: sortedSpaces,
          layout: editingFloor.value === floor && floorDraft.value
            ? floorDraft.value
            : normalizeFloorLayout(storedLayout, sortedSpaces),
          labs: sortedSpaces.filter((space) => ['laboratorio', 'sala_computo'].includes(space.tipo)).length,
          aulas: sortedSpaces.filter((space) => space.tipo === 'aula').length,
        };
      })
      .filter((floor) => !query || floor.spaces.length);
  });

  const activeFloorIndex = computed(() => pisosVisibles.value.findIndex(
    (floor) => String(floor.key) === String(activeFloorKey.value),
  ));
  const activeFloor = computed(() => (
    pisosVisibles.value[activeFloorIndex.value] ?? null
  ));
  const selectDefaultFloor = () => {
    const requestedFloor = normalizeFloorValue(navigation.route?.query?.piso);
    const preferred = pisosVisibles.value.find(
      (floor) => normalizeFloorValue(floor.key) === requestedFloor,
    ) ?? (!navigation.route ? pisosVisibles.value[0] : null);
    activeFloorKey.value = preferred?.key ?? '';
  };
  const writeFloorQuery = (method = 'replace') => {
    if (!navigation.router || !navigation.route) return;
    const query = {
      ...navigation.route.query,
      ciudad: territorio.selectedCity.value || undefined,
      tipo: territorio.selectedCampusType.value || undefined,
      local: territorio.selectedLocalId.value || undefined,
      pabellon: territorio.selectedBuildingId.value || undefined,
    };
    Object.keys(query).forEach((key) => {
      if (query[key] === undefined || query[key] === '') delete query[key];
    });
    if (activeFloorKey.value) query.piso = String(activeFloorKey.value);
    else delete query.piso;
    if (String(navigation.route.query.piso ?? '') === String(query.piso ?? '')) return;
    navigation.router[method]({ query }).catch(() => {
      showToast('No se pudo actualizar el piso en la navegación.', 'error');
    });
  };
  const showPreviousFloor = () => {
    if (editingFloor.value || activeFloorIndex.value <= 0) return;
    selectFloor(pisosVisibles.value[activeFloorIndex.value - 1].key);
  };
  const showNextFloor = () => {
    if (editingFloor.value || activeFloorIndex.value >= pisosVisibles.value.length - 1) return;
    selectFloor(pisosVisibles.value[activeFloorIndex.value + 1].key);
  };

  function selectFloor(floor, method = 'push') {
    if (editingFloor.value) return false;
    const match = pisosVisibles.value.find((item) => String(item.key) === String(floor));
    if (!match) return false;
    activeFloorKey.value = match.key;
    writeFloorQuery(method);
    return true;
  }
  const clearFloorSelection = (method = 'push') => {
    if (editingFloor.value) {
      showToast('Guarda o cancela la edición del croquis antes de cambiar de ubicación.', 'error');
      return false;
    }
    activeFloorKey.value = '';
    writeFloorQuery(method);
    return true;
  };

  const stats = computed(() => ({
    edificios: edificios.value.length,
    pisos: edificios.value.reduce((total, item) => total + item.pisos.length, 0),
    ambientes: currentSpaces.value.length,
    laboratorios: currentSpaces.value.filter((space) => ['laboratorio', 'sala_computo'].includes(space.tipo)).length,
    aulas: currentSpaces.value.filter((space) => space.tipo === 'aula').length,
    equipos: currentSpaces.value.reduce((total, item) => total + Number(item.cantidad_equipos ?? 0), 0),
    alertas: edificios.value.reduce((total, item) => total + item.alertas, 0),
  }));

  const buildingOptions = computed(() => edificios.value.map((building) => ({
    value: building.id,
    label: `${building.codigo} · ${building.nombre}`,
  })));

  const loadCampus = async ({ silent = false } = {}) => {
    const showInitialLoader = !silent || buildingRecords.value.length === 0;
    if (showInitialLoader) loading.value = true;
    if (!silent) error.value = '';
    try {
      const [buildingData, spaceData, localData] = await Promise.all([
        listarTodas(buildingService, { activo: true }),
        listarTodas(spaceService, { activo: true }),
        listarTodas(localService, { activo: true }),
      ]);
      buildingRecords.value = buildingData;
      spaces.value = spaceData;
      localRecords.value = localData;
      refreshSelection();
      return true;
    } catch (requestError) {
      const message = getApiErrorMessage(requestError, 'No se pudo cargar el campus.');
      if (silent) showToast(message, 'error');
      else error.value = message;
      return false;
    } finally {
      if (showInitialLoader) loading.value = false;
    }
  };

  const resetBuildingForm = () => {
    Object.assign(buildingForm, emptyBuilding());
    Object.keys(buildingErrors).forEach((key) => delete buildingErrors[key]);
  };

  const openCreateBuilding = () => {
    if (!canEdit.value || selectionBlocked()) return;
    editingBuilding.value = null;
    resetBuildingForm();
    buildingForm.local_id = territorio.localActivo.value?.id ?? '';
    buildingModalOpen.value = true;
  };

  const openEditBuilding = (building) => {
    if (!canEdit.value || selectionBlocked()) return;
    editingBuilding.value = building;
    resetBuildingForm();
    Object.assign(buildingForm, {
      codigo: building.codigo,
      nombre: building.nombre,
      descripcion: building.descripcion ?? '',
      local_id: building.local_id ?? building.local?.id ?? '',
      activo: building.activo,
    });
    buildingModalOpen.value = true;
  };

  const closeBuildingModal = () => {
    buildingModalOpen.value = false;
    editingBuilding.value = null;
    resetBuildingForm();
  };

  const submitBuilding = async () => {
    if (!canEdit.value || saving.value || selectionBlocked()) return;
    Object.keys(buildingErrors).forEach((key) => delete buildingErrors[key]);
    if (!buildingForm.codigo.trim()) buildingErrors.codigo = 'Ingresa el código.';
    if (!buildingForm.nombre.trim()) buildingErrors.nombre = 'Ingresa el nombre.';
    if (Object.keys(buildingErrors).length) return;
    saving.value = true;
    try {
      const wasCreating = !isEditingBuilding.value;
      const payload = { ...buildingForm, local_id: buildingForm.local_id ? Number(buildingForm.local_id) : null };
      const saved = wasCreating
        ? await buildingService.crear(payload)
        : await buildingService.actualizar(editingBuilding.value.id, payload);
      closeBuildingModal();
      if (!await loadCampus({ silent: true })) return;
      if (saved.activo !== false) selectSavedBuilding(saved);
      showToast(wasCreating ? 'Pabellón agregado al local.' : 'Pabellón actualizado.');
    } catch (requestError) {
      const errors = requestError.response?.data?.errores ?? {};
      for (const field of Object.keys(buildingForm)) {
        if (errors[field]) buildingErrors[field] = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
      }
      showToast(getApiErrorMessage(requestError, 'No se pudo guardar el pabellón.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const askDeleteBuilding = (building) => {
    if (!canEdit.value || selectionBlocked()) return;
    pendingBuildingDelete.value = building;
    buildingDeleteOpen.value = true;
  };
  const cancelDeleteBuilding = () => {
    pendingBuildingDelete.value = null;
    buildingDeleteOpen.value = false;
  };
  const confirmDeleteBuilding = async () => {
    if (!pendingBuildingDelete.value || !canEdit.value || saving.value || selectionBlocked()) return;
    saving.value = true;
    try {
      await buildingService.desactivar(pendingBuildingDelete.value.id);
      cancelDeleteBuilding();
      if (!await loadCampus({ silent: true })) return;
      showToast('Pabellón desactivado. Sus espacios conservaron el historial.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo desactivar el pabellón.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const resetSpaceForm = () => {
    Object.assign(spaceForm, emptySpace(), { edificio_id: edificioActivo.value?.id ?? '' });
    Object.keys(spaceErrors).forEach((key) => delete spaceErrors[key]);
  };
  const openCreateSpace = (floor = '') => {
    if (!canEdit.value) return;
    editingSpace.value = null;
    resetSpaceForm();
    spaceForm.piso = normalizeFloorValue(floor);
    spaceModalOpen.value = true;
  };
  const openEditSpace = (space) => {
    if (!canEdit.value) return;
    editingSpace.value = space;
    resetSpaceForm();
    Object.assign(spaceForm, {
      codigo_espacio: space.codigo_espacio,
      tipo: space.tipo,
      edificio_id: space.edificio_id ?? space.edificio?.id ?? edificioActivo.value?.id,
      piso: normalizeFloorValue(space.piso),
      activo: space.activo,
    });
    spaceModalOpen.value = true;
  };
  const closeSpaceModal = () => {
    spaceModalOpen.value = false;
    editingSpace.value = null;
    resetSpaceForm();
  };
  const submitSpace = async () => {
    if (!canEdit.value || saving.value) return;
    Object.keys(spaceErrors).forEach((key) => delete spaceErrors[key]);
    if (!spaceForm.codigo_espacio.trim()) spaceErrors.codigo_espacio = 'Ingresa el código.';
    if (!spaceForm.edificio_id) spaceErrors.edificio_id = 'Selecciona el pabellón.';
    const normalizedFloor = String(spaceForm.piso ?? '').trim();
    if (!/^\d+$/.test(normalizedFloor)) {
      spaceErrors.piso = 'El piso debe contener únicamente números.';
    }
    if (Object.keys(spaceErrors).length) return;
    saving.value = true;
    try {
      const wasCreating = !isEditingSpace.value;
      const payload = {
        ...spaceForm,
        piso: normalizedFloor,
        edificio_id: Number(spaceForm.edificio_id),
      };
      if (wasCreating) await spaceService.crear(payload);
      else await spaceService.actualizar(editingSpace.value.id, payload);
      closeSpaceModal();
      if (!await loadCampus({ silent: true })) return;
      showToast(wasCreating ? 'Ambiente agregado al piso.' : 'Ambiente actualizado.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo guardar el ambiente.'), 'error');
    } finally {
      saving.value = false;
    }
  };
  const askDeleteSpace = (space) => {
    if (!canEdit.value) return;
    pendingSpaceDelete.value = space;
    spaceDeleteOpen.value = true;
  };
  const cancelDeleteSpace = () => {
    pendingSpaceDelete.value = null;
    spaceDeleteOpen.value = false;
  };
  const confirmDeleteSpace = async () => {
    if (!pendingSpaceDelete.value || !canEdit.value || saving.value) return;
    saving.value = true;
    try {
      await spaceService.desactivar(pendingSpaceDelete.value.id);
      cancelDeleteSpace();
      if (!await loadCampus({ silent: true })) return;
      showToast('Ambiente desactivado correctamente.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo desactivar el ambiente.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const locales = useLocalesCampus({
    service: localService, saving, canEdit, selectionBlocked, loadCampus,
    selectLocal: territorio.selectSavedLocal,
    selectedCity: territorio.selectedCity,
    selectedType: territorio.selectedCampusType,
    showToast,
  });
  const explorerLevel = computed(() => {
    if (activeFloor.value) return 'floor-plan';
    if (territorio.selectedBuildingId.value) return 'floors';
    if (territorio.selectedLocalId.value) return 'buildings';
    if (territorio.selectedCity.value) return 'locals';
    return 'cities';
  });
  const showCities = () => territorio.selectCity('');
  const showLocals = () => territorio.selectCity(territorio.selectedCity.value);
  const showBuildings = () => territorio.selectLocalCard(territorio.selectedLocalId.value);
  const showFloors = () => clearFloorSelection();
  const goBack = () => {
    if (explorerLevel.value === 'floor-plan') return showFloors();
    if (explorerLevel.value === 'floors') return territorio.selectBuilding('');
    if (explorerLevel.value === 'buildings') return showLocals();
    if (explorerLevel.value === 'locals') return showCities();
    return false;
  };
  watch(selectedBuildingId, () => {
    search.value = '';
    cancelFloorEditing();
  });
  watch(
    [selectedBuildingId, () => pisosVisibles.value.map((floor) => floor.key).join('|')],
    ([buildingId], [previousBuildingId] = []) => {
      const floorStillExists = pisosVisibles.value.some(
        (floor) => String(floor.key) === String(activeFloorKey.value),
      );
      if (String(buildingId) !== String(previousBuildingId) || !floorStillExists) {
        selectDefaultFloor();
        territorio.afterNavigation(() => writeFloorQuery('replace'));
      }
    },
  );
  if (navigation.route) {
    watch(() => navigation.route.query.piso, (floor) => {
      const normalized = normalizeFloorValue(floor);
      if (normalized && normalized !== normalizeFloorValue(activeFloorKey.value)) {
        selectFloor(normalized, 'replace');
      } else if (!normalized && activeFloorKey.value) {
        activeFloorKey.value = '';
      }
    });
  }

  const openAssignTechnicianModal = async (target) => {
    if (!canEdit.value) return;
    technicianTarget.value = target;
    technicianForm.assignment_id = target.encargado?.id ?? null;
    technicianForm.usuario_id = target.encargado?.usuario_id ?? '';
    technicianForm.tipo_responsabilidad = target.encargado?.tipo_responsabilidad ?? 'tecnico';
    technicianModalOpen.value = true;

    if (!technicianOptions.value.length) {
      technicianLoading.value = true;
      try {
        const data = await asignacionesService.obtenerOpciones();
        const users = data?.usuarios ?? [];
        technicianOptions.value = users
          .filter((u) => ['tecnico', 'responsable', 'admin'].includes(u.rol))
          .map((u) => ({
            value: u.id,
            label: `${u.nombre} ${u.apellido} (${u.rol}) · ${u.correo}`,
          }));
      } catch {
        technicianOptions.value = [];
      } finally {
        technicianLoading.value = false;
      }
    }
  };

  const submitTechnicianAssignment = async () => {
    if (!technicianForm.usuario_id || !technicianTarget.value || technicianSaving.value) return;
    technicianSaving.value = true;
    const target = technicianTarget.value;
    const payload = {
      usuario_id: Number(technicianForm.usuario_id),
      tipo_responsabilidad: technicianForm.tipo_responsabilidad || 'tecnico',
      activo: true,
      ambito: 'piso',
      local_id: Number(target.local_id),
      edificio_id: Number(target.edificio_id),
      piso: String(target.piso).trim(),
      espacio_id: null,
    };

    try {
      if (technicianForm.assignment_id) {
        await asignacionesService.actualizar(technicianForm.assignment_id, payload);
      } else {
        await asignacionesService.crear(payload);
      }
      technicianModalOpen.value = false;
      showToast('Técnico encargado del piso asignado correctamente.');
      await loadFloorAssignments(target.edificio_id);
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudo asignar el técnico al piso.'), 'error');
    } finally {
      technicianSaving.value = false;
    }
  };

  onMounted(loadCampus);

  return {
    ...territorio, ...locales,
    loading, saving, error, search, edificios, currentSpaces, selectedBuildingId, edificioActivo,
    pisosVisibles, activeFloor, activeFloorIndex, activeFloorKey, stats, canEdit,
    explorerLevel,
    buildingColumnCount, buildingOptions, typeOptions, buildingModalOpen,
    buildingDeleteOpen, editingBuilding, pendingBuildingDelete, buildingForm,
    buildingErrors, isEditingBuilding, spaceModalOpen, spaceDeleteOpen, editingSpace,
    pendingSpaceDelete, spaceForm, spaceErrors, isEditingSpace, toast, loadCampus,
    editingFloor, floorDraft, floorTool, selectedFloorSpaceId, floorSaving,
    floorAssignments, technicianModalOpen, technicianSaving, technicianLoading,
    technicianTarget, technicianOptions, technicianForm,
    openAssignTechnicianModal, submitTechnicianAssignment, loadFloorAssignments,
    openCreateBuilding, openEditBuilding, closeBuildingModal, submitBuilding,
    askDeleteBuilding, cancelDeleteBuilding, confirmDeleteBuilding, openCreateSpace,
    openEditSpace, closeSpaceModal, submitSpace, askDeleteSpace, cancelDeleteSpace,
    confirmDeleteSpace, closeToast: () => { toast.show = false; },
    startFloorEditing, cancelFloorEditing, selectFloorSpace, handleFloorCell,
    setFloorTool,
    resizeSelectedFloorSpace, updateFloorColumns, addFloorRow, removeFloorRow,
    saveFloorLayout, showPreviousFloor, showNextFloor, selectFloor, clearFloorSelection,
    showCities, showLocals, showBuildings, showFloors, goBack,
  };
}
