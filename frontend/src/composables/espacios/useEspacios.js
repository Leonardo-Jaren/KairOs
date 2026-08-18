import { computed, onMounted, reactive, ref } from 'vue';

import espaciosService from '@/services/espacios.service';
import edificiosService from '@/services/edificios.service';
import { useAutoFilters } from '@/composables/shared/useAutoFilters';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  codigo_espacio: '',
  tipo: 'laboratorio',
  edificio_id: '',
  piso: '',
  activo: true,
});

export function useEspacios(service = espaciosService, buildingService = edificiosService) {
  const authStore = useAuthStore();
  const espacios = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const modalOpen = ref(false);
  const deleteModalOpen = ref(false);
  const editingSpace = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const formErrors = reactive({});
  const filters = reactive({ search: '', tipo: '', activo: '', page: 1, page_size: 10 });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const stats = reactive({ total: 0, activos: 0, laboratorios: 0, equipos: 0 });
  const toast = reactive({ show: false, message: '', type: 'success' });
  const buildings = ref([]);

  const canEdit = computed(() => authStore.user?.rol === 'admin');
  const isEditing = computed(() => Boolean(editingSpace.value));
  const typeOptions = [
    { value: 'laboratorio', label: 'Laboratorio' },
    { value: 'oficina', label: 'Oficina' },
    { value: 'aula', label: 'Aula' },
    { value: 'sala_computo', label: 'Sala de cómputo' },
    { value: 'otro', label: 'Otro' },
  ];
  const buildingOptions = computed(() => buildings.value.map((building) => ({
    value: building.id,
    label: `${building.codigo} · ${building.nombre}`,
  })));

  const loadSpaces = async () => {
    loading.value = true;
    try {
      const data = await service.listar(filters);
      espacios.value = data.results ?? data;
      pagination.total = data.count ?? espacios.value.length;
      pagination.totalPages = Math.max(1, Math.ceil(pagination.total / filters.page_size));
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los espacios.'), 'error');
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

  const loadBuildings = async () => {
    try {
      const data = await buildingService.listar({ activo: true, page_size: 100 });
      buildings.value = data.results ?? data;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los edificios.'), 'error');
    }
  };
  const loadData = () => Promise.all([loadSpaces(), loadStats(), loadBuildings()]);
  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };
  const openCreate = () => {
    editingSpace.value = null;
    resetForm();
    modalOpen.value = true;
  };
  const openEdit = (space) => {
    editingSpace.value = space;
    resetForm();
    Object.assign(form, {
      codigo_espacio: space.codigo_espacio,
      tipo: space.tipo,
      edificio_id: space.edificio_id ?? space.edificio?.id ?? '',
      piso: space.piso,
      activo: space.activo,
    });
    modalOpen.value = true;
  };
  const closeModal = () => {
    modalOpen.value = false;
    editingSpace.value = null;
    resetForm();
  };
  const validateForm = () => {
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
    if (!form.codigo_espacio.trim()) formErrors.codigo_espacio = 'Ingresa el código del espacio.';
    if (!form.tipo) formErrors.tipo = 'Selecciona el tipo de espacio.';
    if (!form.edificio_id) formErrors.edificio_id = 'Selecciona un edificio.';
    if (!/^\d+$/.test(String(form.piso ?? '').trim())) {
      formErrors.piso = 'El piso debe contener únicamente números.';
    }
    return Object.keys(formErrors).length === 0;
  };
  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;
    const payload = { ...form, piso: String(form.piso).trim() };
    try {
      if (isEditing.value) {
        await service.actualizar(editingSpace.value.id, payload);
        showToast('Espacio actualizado correctamente.');
      } else {
        await service.crear(payload);
        showToast('Espacio creado correctamente.');
      }
      closeModal();
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo guardar el espacio.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };
  const askDelete = (space) => {
    pendingDelete.value = space;
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
      await service.desactivar(pendingDelete.value.id);
      showToast('Espacio desactivado correctamente.');
      cancelDelete();
      await loadData();
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo desactivar el espacio.'), 'error');
    } finally {
      saving.value = false;
    }
  };
  const { applyFilters, resetFilters } = useAutoFilters(filters, loadSpaces, {
    immediateKeys: ['tipo', 'activo'],
  });
  const clearFilters = () => resetFilters({ search: '', tipo: '', activo: '' });
  const changePage = (page) => {
    filters.page = page;
    return loadSpaces();
  };
  const showToast = (message, type = 'success') => Object.assign(toast, { show: true, message, type });
  const closeToast = () => { toast.show = false; };

  onMounted(loadData);

  return {
    espacios, loading, saving, modalOpen, deleteModalOpen, pendingDelete,
    form, formErrors, filters, pagination, stats, toast, canEdit, isEditing,
    typeOptions, buildingOptions, loadSpaces, openCreate, openEdit, closeModal, submit,
    askDelete, cancelDelete, confirmDelete, applyFilters, clearFilters,
    changePage, closeToast,
  };
}
