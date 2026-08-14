import { computed, onMounted, reactive, ref, watch } from 'vue';

import edificiosService from '@/services/edificios.service';
import espaciosService from '@/services/espacios.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';
import { formatFloor } from '@/utils/formatters';

const naturalCompare = (left, right) => String(left).localeCompare(String(right), 'es', {
  numeric: true,
  sensitivity: 'base',
});

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
    const floors = [...new Set(buildingSpaces.map((space) => space.piso))].sort(naturalCompare);
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

  const edificioActivo = computed(() => (
    edificios.value.find((building) => String(building.id) === String(selectedBuildingId.value))
    ?? edificios.value[0]
    ?? null
  ));

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
    filtered.forEach((space) => {
      if (!groups.has(space.piso)) groups.set(space.piso, []);
      groups.get(space.piso).push(space);
    });
    return [...groups.entries()]
      .sort(([left], [right]) => naturalCompare(left, right))
      .map(([floor, floorSpaces]) => ({
        key: floor,
        label: formatFloor(floor),
        spaces: floorSpaces.sort((left, right) => naturalCompare(left.codigo_espacio, right.codigo_espacio)),
        labs: floorSpaces.filter((space) => ['laboratorio', 'sala_computo'].includes(space.tipo)).length,
        aulas: floorSpaces.filter((space) => space.tipo === 'aula').length,
      }));
  });

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

  const showToast = (message, type = 'success') => Object.assign(toast, { show: true, message, type });

  const loadCampus = async () => {
    loading.value = true;
    error.value = '';
    try {
      const [buildingData, spaceData] = await Promise.all([
        buildingService.listar({ activo: true, page_size: 100 }),
        spaceService.listar({ activo: true, page_size: 200 }),
      ]);
      buildingRecords.value = buildingData.results ?? buildingData;
      spaces.value = spaceData.results ?? spaceData;
    } catch (requestError) {
      error.value = getApiErrorMessage(requestError, 'No se pudo cargar el campus.');
    } finally {
      loading.value = false;
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
      await loadCampus();
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
      await loadCampus();
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
    spaceForm.piso = floor;
    spaceModalOpen.value = true;
  };
  const openEditSpace = (space) => {
    editingSpace.value = space;
    resetSpaceForm();
    Object.assign(spaceForm, {
      codigo_espacio: space.codigo_espacio,
      tipo: space.tipo,
      edificio_id: space.edificio_id ?? space.edificio?.id ?? edificioActivo.value?.id,
      piso: space.piso,
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
    if (!spaceForm.piso.trim()) spaceErrors.piso = 'Ingresa el piso.';
    if (Object.keys(spaceErrors).length) return;
    saving.value = true;
    try {
      const wasCreating = !isEditingSpace.value;
      const payload = { ...spaceForm, edificio_id: Number(spaceForm.edificio_id) };
      if (wasCreating) await spaceService.crear(payload);
      else await spaceService.actualizar(editingSpace.value.id, payload);
      closeSpaceModal();
      await loadCampus();
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
      await loadCampus();
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

  onMounted(loadCampus);

  return {
    loading, saving, error, search, edificios, selectedBuildingId, edificioActivo,
    pisosVisibles, stats, canEdit, buildingOptions, typeOptions, buildingModalOpen,
    buildingDeleteOpen, editingBuilding, pendingBuildingDelete, buildingForm,
    buildingErrors, isEditingBuilding, spaceModalOpen, spaceDeleteOpen, editingSpace,
    pendingSpaceDelete, spaceForm, spaceErrors, isEditingSpace, toast, loadCampus,
    openCreateBuilding, openEditBuilding, closeBuildingModal, submitBuilding,
    askDeleteBuilding, cancelDeleteBuilding, confirmDeleteBuilding, openCreateSpace,
    openEditSpace, closeSpaceModal, submitSpace, askDeleteSpace, cancelDeleteSpace,
    confirmDeleteSpace, closeToast: () => { toast.show = false; },
  };
}
