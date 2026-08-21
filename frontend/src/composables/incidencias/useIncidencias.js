import { computed, onMounted, reactive, ref } from 'vue';

import incidenciasService from '@/services/incidencias.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  espacio: '',
  equipo: '',
  tipo_incidencia: 'hardware',
  descripcion: '',
  estado: 'pendiente',
});

export const TIPO_INCIDENCIA_OPTIONS = [
  { value: 'hardware', label: 'Hardware' },
  { value: 'software', label: 'Software' },
];

export const ESTADO_OPTIONS = [
  { value: 'pendiente', label: 'Pendiente' },
  { value: 'en_proceso', label: 'En Proceso' },
  { value: 'resuelto', label: 'Resuelto' },
];

export function useIncidencias(service = incidenciasService) {
  const authStore = useAuthStore();
  const incidencias = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const modalOpen = ref(false);
  const deleteModalOpen = ref(false);
  const editingIncidencia = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const formErrors = reactive({});
  const toast = reactive({ show: false, message: '', type: 'success' });
  const filters = reactive({
    search: '', espacio_id: '', equipo_id: '', tipo_incidencia: '', estado: '', page: 1, page_size: 8,
  });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const stats = reactive({ total: 0, pendientes: 0, en_proceso: 0, resueltas: 0 });
  const espacioOptions = ref([]);
  const equipoOptions = ref([]);

  const isEditing = computed(() => Boolean(editingIncidencia.value));
  const canManageAll = computed(() => ['admin', 'tecnico'].includes(authStore.user?.rol));

  const espacioSelectOptions = computed(() => espacioOptions.value.map((espacio) => ({
    value: espacio.id,
    label: `${espacio.codigo_espacio} · ${espacio.pabellon}`,
  })));

  const equipoSelectOptions = computed(() => equipoOptions.value.map((equipo) => ({
    value: equipo.id,
    label: `${equipo.codigo} · ${equipo.marca} ${equipo.modelo}`,
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
      const [espacios, equipos] = await Promise.all([
        service.obtenerEspaciosOpciones(),
        service.obtenerEquiposOpciones(),
      ]);
      espacioOptions.value = espacios;
      equipoOptions.value = equipos;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar espacios y equipos.'), 'error');
    }
  };

  const loadData = () => Promise.all([loadIncidencias(), loadStats(), loadOpciones()]);

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
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
      descripcion: incidencia.descripcion,
      estado: incidencia.estado,
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
    if (!form.descripcion.trim()) formErrors.descripcion = 'Describe la incidencia.';
    return Object.keys(formErrors).length === 0;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;

    const payload = { ...form, descripcion: form.descripcion.trim() };

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

  const applyFilters = () => {
    filters.page = 1;
    return loadIncidencias();
  };

  const clearFilters = () => {
    Object.assign(filters, {
      search: '', espacio_id: '', equipo_id: '', tipo_incidencia: '', estado: '', page: 1,
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

  return {
    incidencias,
    loading,
    saving,
    modalOpen,
    deleteModalOpen,
    pendingDelete,
    form,
    formErrors,
    filters,
    pagination,
    stats,
    toast,
    isEditing,
    canManageAll,
    tipoIncidenciaOptions: TIPO_INCIDENCIA_OPTIONS,
    estadoOptions: ESTADO_OPTIONS,
    espacioSelectOptions,
    equipoSelectOptions,
    openCreate,
    openEdit,
    closeModal,
    submit,
    askDelete,
    cancelDelete,
    confirmDelete,
    applyFilters,
    clearFilters,
    changePage,
    closeToast,
  };
}
