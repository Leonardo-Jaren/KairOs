import { computed, onMounted, reactive, ref, watch } from 'vue';

import incidenciasService from '@/services/incidencias.service';
import historialService from '@/services/historial.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  espacio: '',
  equipo: '',
  tipo_incidencia: 'hardware',
  prioridad: 'media',
  descripcion: '',
  estado: 'pendiente',
  asignado_a: '',
  resolucion: '',
  motivo_cierre: '',
});

export const TIPO_INCIDENCIA_OPTIONS = [
  { value: 'hardware', label: 'Hardware' },
  { value: 'software', label: 'Software' },
];

export const ESTADO_OPTIONS = [
  { value: 'pendiente', label: 'Pendiente de atención' },
  { value: 'en_proceso', label: 'En atención' },
  { value: 'resuelto', label: 'Resuelta' },
  { value: 'cerrado', label: 'Cerrado' },
  { value: 'cancelado', label: 'Cancelado' },
  { value: 'duplicado', label: 'Duplicado' },
];

export const PRIORIDAD_OPTIONS = [
  { value: 'baja', label: 'Baja' },
  { value: 'media', label: 'Media' },
  { value: 'alta', label: 'Alta' },
  { value: 'critica', label: 'Crítica' },
];

export function useIncidencias(service = incidenciasService) {
  const authStore = useAuthStore();
  const incidencias = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const correctiveSaving = ref(false);
  const modalOpen = ref(false);
  const deleteModalOpen = ref(false);
  const detailOpen = ref(false);
  const detailLoading = ref(false);
  const selectedIncidencia = ref(null);
  const detailEvents = ref([]);
  const detailMaintenances = ref([]);
  const editingIncidencia = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const formErrors = reactive({});
  const toast = reactive({ show: false, message: '', type: 'success' });
  const filters = reactive({
    search: '', espacio_id: '', equipo_id: '', tipo_incidencia: '', prioridad: '', estado: '',
    asignado_a_id: '', page: 1, page_size: 8,
  });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const stats = reactive({ total: 0, pendientes: 0, en_proceso: 0, resueltas: 0 });
  const espacioOptions = ref([]);
  const equipoOptions = ref([]);
  const formEquipoOptions = ref([]);
  const tecnicoOptions = ref([]);

  const isEditing = computed(() => Boolean(editingIncidencia.value));
  const canManageAll = computed(() => authStore.hasPermission('incidencias', 'editar'));
  const canCreate = computed(() => authStore.hasPermission('incidencias', 'crear'));
  const canDelete = computed(() => authStore.hasPermission('incidencias', 'eliminar'));

  const espacioSelectOptions = computed(() => espacioOptions.value.map((espacio) => ({
    value: espacio.id,
    label: `${espacio.codigo_espacio} · ${espacio.pabellon}`,
  })));

  const equipoSelectOptions = computed(() => equipoOptions.value.map((equipo) => ({
    value: equipo.id,
    label: `${equipo.codigo} · ${equipo.marca} ${equipo.modelo}`,
  })));

  const formEquipoSelectOptions = computed(() => formEquipoOptions.value.map((equipo) => ({
    value: equipo.id,
    label: `${equipo.codigo} · ${equipo.marca} ${equipo.modelo}`,
  })));

  const tecnicoSelectOptions = computed(() => tecnicoOptions.value.map((tecnico) => ({
    value: tecnico.id,
    label: `${tecnico.nombre_completo} (${tecnico.area})`,
  })));

  const loadIncidencias = async () => {
    loading.value = true;
    try {
      const data = await service.listar(filters);
      incidencias.value = data.results ?? data;
      pagination.total = data.count ?? incidencias.value.length;
      pagination.totalPages = Math.max(1, Math.ceil(pagination.total / filters.page_size));
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar las incidencias.'), 'error');
    } finally {
      loading.value = false;
    }
  };

  const loadStats = async () => {
    try {
      Object.assign(stats, await service.obtenerEstadisticas());
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los indicadores.'), 'error');
    }
  };

  const loadOpciones = async () => {
    try {
      const requests = [
        service.obtenerEspaciosOpciones(),
        service.obtenerEquiposOpciones(),
      ];
      if (canManageAll.value) requests.push(service.obtenerTecnicosDisponibles());
      const [espacios, equipos, tecnicos = []] = await Promise.all(requests);
      espacioOptions.value = espacios;
      equipoOptions.value = equipos;
      formEquipoOptions.value = equipos;
      tecnicoOptions.value = tecnicos;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar espacios y equipos.'), 'error');
    }
  };

  const loadData = () => Promise.all([loadIncidencias(), loadStats(), loadOpciones()]);

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };

  const loadFormEquipos = async (espacioId) => {
    if (!espacioId) {
      formEquipoOptions.value = [];
      return;
    }
    try {
      formEquipoOptions.value = await service.obtenerEquiposOpciones(espacioId);
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los equipos del espacio.'), 'error');
    }
  };

  const openCreate = () => {
    editingIncidencia.value = null;
    resetForm();
    modalOpen.value = true;
  };

  const openEdit = (incidencia) => {
    editingIncidencia.value = incidencia;
    resetForm();
    Object.assign(form, {
      espacio: incidencia.espacio,
      equipo: incidencia.equipo,
      tipo_incidencia: incidencia.tipo_incidencia,
      prioridad: incidencia.prioridad ?? 'media',
      descripcion: incidencia.descripcion,
      estado: incidencia.estado,
      asignado_a: incidencia.tecnico_asignado?.id ?? '',
      resolucion: incidencia.resolucion ?? '',
      motivo_cierre: incidencia.motivo_cierre ?? '',
    });
    modalOpen.value = true;
  };

  const closeModal = () => {
    modalOpen.value = false;
    editingIncidencia.value = null;
    resetForm();
  };

  const validateForm = () => {
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
    if (!form.espacio) formErrors.espacio = 'Selecciona el espacio.';
    if (!form.equipo) formErrors.equipo = 'Selecciona el equipo.';
    if (!form.tipo_incidencia) formErrors.tipo_incidencia = 'Selecciona el tipo de incidencia.';
    if (!form.prioridad) formErrors.prioridad = 'Selecciona la prioridad.';
    if (!form.descripcion.trim()) formErrors.descripcion = 'Describe la incidencia.';
    if (isEditing.value && ['resuelto', 'cerrado'].includes(form.estado) && !form.resolucion.trim()) {
      formErrors.resolucion = 'Describe cómo se resolvió la incidencia.';
    }
    if (isEditing.value && ['cancelado', 'duplicado'].includes(form.estado) && !form.motivo_cierre.trim()) {
      formErrors.motivo_cierre = 'Indica el motivo de cierre.';
    }
    return Object.keys(formErrors).length === 0;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;

    const payload = {
      espacio: Number(form.espacio),
      equipo: Number(form.equipo),
      tipo_incidencia: form.tipo_incidencia,
      prioridad: form.prioridad,
      descripcion: form.descripcion.trim(),
    };
    if (isEditing.value) {
      Object.assign(payload, {
        estado: form.estado,
        asignado_a: form.asignado_a ? Number(form.asignado_a) : null,
        resolucion: form.resolucion.trim(),
        motivo_cierre: form.motivo_cierre.trim(),
      });
    }

    try {
      if (isEditing.value) {
        await service.actualizar(editingIncidencia.value.id, payload);
        showToast('Incidencia actualizada correctamente.');
      } else {
        await service.crear(payload);
        showToast('Incidencia reportada correctamente.');
      }
      closeModal();
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo guardar la incidencia.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDelete = (incidencia) => {
    pendingDelete.value = incidencia;
    deleteModalOpen.value = true;
  };

  const cancelDelete = () => {
    pendingDelete.value = null;
    deleteModalOpen.value = false;
  };

  const confirmDelete = async () => {
    if (!pendingDelete.value) return;
    saving.value = true;
    try {
      await service.eliminar(pendingDelete.value.id);
      showToast('Incidencia eliminada correctamente.');
      cancelDelete();
      await loadData();
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo eliminar la incidencia.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const attendIncident = async (incidencia) => {
    if (!incidencia || !canManageAll.value) return false;
    saving.value = true;
    try {
      await service.atender(incidencia.id);
      showToast(`INC-${incidencia.id} está en atención.`);
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo iniciar la atención.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const closeIncident = async (incidencia) => {
    if (!incidencia || !canManageAll.value || incidencia.estado !== 'resuelto') return false;
    saving.value = true;
    try {
      const updated = await service.cerrar(incidencia.id);
      if (selectedIncidencia.value?.id === incidencia.id) {
        selectedIncidencia.value = updated;
      }
      showToast(`INC-${incidencia.id} cerrada correctamente.`);
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo cerrar la incidencia.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const openDetail = async (incidencia) => {
    selectedIncidencia.value = incidencia;
    detailOpen.value = true;
    detailLoading.value = true;
    try {
      const [maintenances, events] = await Promise.all([
        service.obtenerMantenimientos(incidencia.id),
        historialService.listar({ modulo: 'incidencia', object_id: incidencia.id, page_size: 50 }),
      ]);
      detailMaintenances.value = maintenances.results ?? maintenances;
      detailEvents.value = events.results ?? events;
    } catch (error) {
      detailMaintenances.value = [];
      detailEvents.value = [];
      showToast(getApiErrorMessage(error, 'No se pudo cargar el detalle de la incidencia.'), 'error');
    } finally {
      detailLoading.value = false;
    }
  };

  const closeDetail = () => {
    detailOpen.value = false;
    selectedIncidencia.value = null;
    detailMaintenances.value = [];
    detailEvents.value = [];
  };

  const createCorrective = async (incidencia) => {
    if (!incidencia || !canManageAll.value) return false;
    correctiveSaving.value = true;
    try {
      await service.crearMantenimiento(incidencia.id, {
        descripcion: `Atención correctiva derivada de la incidencia INC-${incidencia.id}.`,
      });
      showToast('Mantenimiento correctivo creado y vinculado.');
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo crear el mantenimiento correctivo.'), 'error');
      return false;
    } finally {
      correctiveSaving.value = false;
    }
  };

  const applyFilters = () => {
    filters.page = 1;
    return loadIncidencias();
  };

  const clearFilters = () => {
    Object.assign(filters, {
      search: '', espacio_id: '', equipo_id: '', tipo_incidencia: '', prioridad: '', estado: '',
      asignado_a_id: '', page: 1,
    });
    return loadIncidencias();
  };

  const changePage = (page) => {
    filters.page = page;
    return loadIncidencias();
  };

  const showToast = (message, type = 'success') => {
    Object.assign(toast, { show: true, message, type });
  };

  const closeToast = () => {
    toast.show = false;
  };

  onMounted(loadData);

  watch(() => form.espacio, (value) => {
    if (modalOpen.value) loadFormEquipos(value);
  });

  return {
    incidencias,
    loading,
    saving,
    correctiveSaving,
    modalOpen,
    deleteModalOpen,
    detailOpen,
    detailLoading,
    selectedIncidencia,
    detailEvents,
    detailMaintenances,
    pendingDelete,
    form,
    formErrors,
    filters,
    pagination,
    stats,
    toast,
    isEditing,
    canManageAll,
    canCreate,
    canDelete,
    tipoIncidenciaOptions: TIPO_INCIDENCIA_OPTIONS,
    estadoOptions: ESTADO_OPTIONS,
    espacioSelectOptions,
    equipoSelectOptions,
    formEquipoSelectOptions,
    tecnicoSelectOptions,
    prioridadOptions: PRIORIDAD_OPTIONS,
    loadFormEquipos,
    openCreate,
    openEdit,
    closeModal,
    openDetail,
    closeDetail,
    submit,
    attendIncident,
    closeIncident,
    askDelete,
    cancelDelete,
    confirmDelete,
    createCorrective,
    applyFilters,
    clearFilters,
    changePage,
    closeToast,
  };
}
