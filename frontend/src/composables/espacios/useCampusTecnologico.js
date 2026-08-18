import { computed, onMounted, reactive, ref, watch } from 'vue';

import edificiosService from '@/services/edificios.service';
import espaciosService from '@/services/espacios.service';
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

const emptyBuilding = () => ({ codigo: '', nombre: '', descripcion: '', activo: true });
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
) {
  const authStore = useAuthStore();
  const spaces = ref([]);
  const buildingRecords = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const error = ref('');
  const search = ref('');
  const selectedBuildingId = ref('');
  const activeFloorKey = ref('');
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

  const canEdit = computed(() => authStore.user?.rol === 'admin');
  const isEditingBuilding = computed(() => Boolean(editingBuilding.value));
  const isEditingSpace = computed(() => Boolean(editingSpace.value));
  const typeOptions = [
    { value: 'laboratorio', label: 'Laboratorio' },
    { value: 'sala_computo', label: 'Sala de cómputo' },
    { value: 'aula', label: 'Aula' },
    { value: 'oficina', label: 'Oficina' },
    { value: 'otro', label: 'Otro' },
  ];

  const edificios = computed(() => buildingRecords.value.map((building) => {
    const buildingSpaces = spaces.value.filter((space) => (
      Number(space.edificio_id ?? space.edificio?.id) === building.id
    ));
    const floors = [...new Set(buildingSpaces.map((space) => normalizeFloorValue(space.piso)))].sort(naturalCompare);
    return {
      ...building,
      spaces: buildingSpaces,
      pisos: floors,
      laboratorios: buildingSpaces.filter((space) => ['laboratorio', 'sala_computo'].includes(space.tipo)),
      aulas: buildingSpaces.filter((space) => space.tipo === 'aula'),
      equipos: buildingSpaces.reduce((total, space) => total + space.cantidad_equipos, 0),
      alertas: buildingSpaces.reduce((total, space) => (
        total + (space.resumen_equipos?.en_mantenimiento ?? 0) + (space.resumen_equipos?.dañado ?? 0)
      ), 0),
    };
  }));
  const buildingColumnCount = computed(() => {
    const count = edificios.value.length;
    if (count <= 1) return 1;
    const candidates = Array.from({ length: Math.min(6, count) - 1 }, (_, index) => index + 2);
    return candidates.reduce((best, columns) => {
      const emptyCells = Math.ceil(count / columns) * columns - count;
      const bestEmptyCells = Math.ceil(count / best) * best - count;
      return emptyCells < bestEmptyCells || (emptyCells === bestEmptyCells && columns > best)
        ? columns
        : best;
    }, 2);
  });

  const edificioActivo = computed(() => (
    edificios.value.find((building) => String(building.id) === String(selectedBuildingId.value))
    ?? edificios.value[0]
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
          label: formatFloor(floor),
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
    const preferred = pisosVisibles.value.find(
      (floor) => normalizeFloorValue(floor.key) === '2',
    ) ?? pisosVisibles.value[1] ?? pisosVisibles.value[0];
    activeFloorKey.value = preferred?.key ?? '';
  };
  const showPreviousFloor = () => {
    if (editingFloor.value || activeFloorIndex.value <= 0) return;
    activeFloorKey.value = pisosVisibles.value[activeFloorIndex.value - 1].key;
  };
  const showNextFloor = () => {
    if (editingFloor.value || activeFloorIndex.value >= pisosVisibles.value.length - 1) return;
    activeFloorKey.value = pisosVisibles.value[activeFloorIndex.value + 1].key;
  };

  const stats = computed(() => ({
    edificios: edificios.value.length,
    ambientes: spaces.value.length,
    laboratorios: spaces.value.filter((space) => ['laboratorio', 'sala_computo'].includes(space.tipo)).length,
    aulas: spaces.value.filter((space) => space.tipo === 'aula').length,
    equipos: spaces.value.reduce((total, item) => total + item.cantidad_equipos, 0),
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
      const [buildingData, spaceData] = await Promise.all([
        buildingService.listar({ activo: true, page_size: 100 }),
        spaceService.listar({ activo: true, page_size: 200 }),
      ]);
      buildingRecords.value = buildingData.results ?? buildingData;
      spaces.value = spaceData.results ?? spaceData;
    } catch (requestError) {
      const message = getApiErrorMessage(requestError, 'No se pudo cargar el campus.');
      if (silent) showToast(message, 'error');
      else error.value = message;
    } finally {
      if (showInitialLoader) loading.value = false;
    }
  };

  const resetBuildingForm = () => {
    Object.assign(buildingForm, emptyBuilding());
    Object.keys(buildingErrors).forEach((key) => delete buildingErrors[key]);
  };

  const openCreateBuilding = () => {
    editingBuilding.value = null;
    resetBuildingForm();
    buildingModalOpen.value = true;
  };

  const openEditBuilding = (building) => {
    editingBuilding.value = building;
    resetBuildingForm();
    Object.assign(buildingForm, {
      codigo: building.codigo,
      nombre: building.nombre,
      descripcion: building.descripcion ?? '',
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
    Object.keys(buildingErrors).forEach((key) => delete buildingErrors[key]);
    if (!buildingForm.codigo.trim()) buildingErrors.codigo = 'Ingresa el código.';
    if (!buildingForm.nombre.trim()) buildingErrors.nombre = 'Ingresa el nombre.';
    if (Object.keys(buildingErrors).length) return;
    saving.value = true;
    try {
      const wasCreating = !isEditingBuilding.value;
      const payload = { ...buildingForm };
      const saved = wasCreating
        ? await buildingService.crear(payload)
        : await buildingService.actualizar(editingBuilding.value.id, payload);
      closeBuildingModal();
      await loadCampus({ silent: true });
      selectedBuildingId.value = saved.id;
      showToast(wasCreating ? 'Edificio agregado al campus.' : 'Edificio actualizado.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo guardar el edificio.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const askDeleteBuilding = (building) => {
    pendingBuildingDelete.value = building;
    buildingDeleteOpen.value = true;
  };
  const cancelDeleteBuilding = () => {
    pendingBuildingDelete.value = null;
    buildingDeleteOpen.value = false;
  };
  const confirmDeleteBuilding = async () => {
    if (!pendingBuildingDelete.value) return;
    saving.value = true;
    try {
      await buildingService.desactivar(pendingBuildingDelete.value.id);
      cancelDeleteBuilding();
      await loadCampus({ silent: true });
      showToast('Edificio desactivado. Sus espacios conservaron el historial.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo desactivar el edificio.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const resetSpaceForm = () => {
    Object.assign(spaceForm, emptySpace(), { edificio_id: edificioActivo.value?.id ?? '' });
    Object.keys(spaceErrors).forEach((key) => delete spaceErrors[key]);
  };
  const openCreateSpace = (floor = '') => {
    editingSpace.value = null;
    resetSpaceForm();
    spaceForm.piso = normalizeFloorValue(floor);
    spaceModalOpen.value = true;
  };
  const openEditSpace = (space) => {
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
    Object.keys(spaceErrors).forEach((key) => delete spaceErrors[key]);
    if (!spaceForm.codigo_espacio.trim()) spaceErrors.codigo_espacio = 'Ingresa el código.';
    if (!spaceForm.edificio_id) spaceErrors.edificio_id = 'Selecciona el edificio.';
    const normalizedFloor = normalizeFloorValue(spaceForm.piso);
    if (!normalizedFloor) spaceErrors.piso = 'Ingresa el número o nombre corto del piso.';
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
      await loadCampus({ silent: true });
      showToast(wasCreating ? 'Ambiente agregado al piso.' : 'Ambiente actualizado.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo guardar el ambiente.'), 'error');
    } finally {
      saving.value = false;
    }
  };
  const askDeleteSpace = (space) => {
    pendingSpaceDelete.value = space;
    spaceDeleteOpen.value = true;
  };
  const cancelDeleteSpace = () => {
    pendingSpaceDelete.value = null;
    spaceDeleteOpen.value = false;
  };
  const confirmDeleteSpace = async () => {
    if (!pendingSpaceDelete.value) return;
    saving.value = true;
    try {
      await spaceService.desactivar(pendingSpaceDelete.value.id);
      cancelDeleteSpace();
      await loadCampus({ silent: true });
      showToast('Ambiente desactivado correctamente.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo desactivar el ambiente.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  watch(edificios, (items) => {
    if (!items.some((item) => String(item.id) === String(selectedBuildingId.value))) {
      selectedBuildingId.value = items[0]?.id ?? '';
    }
  }, { immediate: true });

  watch(selectedBuildingId, cancelFloorEditing);
  watch(
    [selectedBuildingId, () => pisosVisibles.value.map((floor) => floor.key).join('|')],
    ([buildingId], [previousBuildingId] = []) => {
      const floorStillExists = pisosVisibles.value.some(
        (floor) => String(floor.key) === String(activeFloorKey.value),
      );
      if (String(buildingId) !== String(previousBuildingId) || !floorStillExists) {
        selectDefaultFloor();
      }
    },
    { immediate: true },
  );

  onMounted(loadCampus);

  return {
    loading, saving, error, search, edificios, selectedBuildingId, edificioActivo,
    pisosVisibles, activeFloor, activeFloorIndex, activeFloorKey, stats, canEdit,
    buildingColumnCount, buildingOptions, typeOptions, buildingModalOpen,
    buildingDeleteOpen, editingBuilding, pendingBuildingDelete, buildingForm,
    buildingErrors, isEditingBuilding, spaceModalOpen, spaceDeleteOpen, editingSpace,
    pendingSpaceDelete, spaceForm, spaceErrors, isEditingSpace, toast, loadCampus,
    editingFloor, floorDraft, floorTool, selectedFloorSpaceId, floorSaving,
    openCreateBuilding, openEditBuilding, closeBuildingModal, submitBuilding,
    askDeleteBuilding, cancelDeleteBuilding, confirmDeleteBuilding, openCreateSpace,
    openEditSpace, closeSpaceModal, submitSpace, askDeleteSpace, cancelDeleteSpace,
    confirmDeleteSpace, closeToast: () => { toast.show = false; },
    startFloorEditing, cancelFloorEditing, selectFloorSpace, handleFloorCell,
    setFloorTool,
    resizeSelectedFloorSpace, updateFloorColumns, addFloorRow, removeFloorRow,
    saveFloorLayout, showPreviousFloor, showNextFloor,
  };
}
