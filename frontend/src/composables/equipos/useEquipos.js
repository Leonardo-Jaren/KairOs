import { computed, onMounted, reactive, ref } from 'vue';

import equiposService from '@/services/equipos.service';
import espaciosService from '@/services/espacios.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  espacio: '',
  codigo: '',
  numero_serie: '',
  numero_mac: '',
  tipo_equipo: 'desktop',
  marca: '',
  modelo: '',
  modo_adquisicion: 'comprado',
  fecha_adquisicion: '',
  fecha_renovacion: '',
  estado: 'en_uso',
  responsable_usuario: '',
});

export function useEquipos(service = equiposService, espaciosServiceInstance = espaciosService) {
  const authStore = useAuthStore();
  const equipos = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const modalOpen = ref(false);
  const deleteModalOpen = ref(false);
  const editingEquipo = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const formErrors = reactive({});
  const toast = reactive({ show: false, message: '', type: 'success' });
  const filters = reactive({ search: '', tipo_equipo: '', estado: '', page: 1, page_size: 8 });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const stats = reactive({ total: 0, en_uso: 0, en_mantenimiento: 0, de_baja: 0 });
  const espacioOptions = ref([]);

  const isEditing = computed(() => Boolean(editingEquipo.value));
  const canManageAll = computed(() => authStore.user?.rol === 'admin');

  const tipoEquipoOptions = [
    { value: 'desktop', label: 'Desktop' },
    { value: 'laptop', label: 'Laptop' },
    { value: 'servidor', label: 'Servidor' },
    { value: 'impresora', label: 'Impresora' },
    { value: 'proyector', label: 'Proyector' },
    { value: 'monitor', label: 'Monitor' },
    { value: 'otro', label: 'Otro' },
  ];

  const modoAdquisicionOptions = [
    { value: 'comprado', label: 'Comprado' },
    { value: 'arrendado', label: 'Arrendado' },
    { value: 'donado', label: 'Donado' },
  ];

  const estadoOptions = [
    { value: 'en_uso', label: 'En uso' },
    { value: 'en_mantenimiento', label: 'En mantenimiento' },
    { value: 'dañado', label: 'Dañado' },
    { value: 'de_baja', label: 'De baja' },
  ];

  const espacioSelectOptions = computed(() => espacioOptions.value.map((espacio) => ({
    value: espacio.id,
    label: `${espacio.codigo_espacio} · ${espacio.pabellon}`,
  })));

  const loadEquipos = async () => {
    loading.value = true;
    try {
      const data = await service.listar(filters);
      equipos.value = data.results ?? data;
      pagination.total = data.count ?? equipos.value.length;
      pagination.totalPages = Math.max(1, Math.ceil(pagination.total / filters.page_size));
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los equipos.'), 'error');
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

  const loadEspacios = async () => {
    try {
      const data = await espaciosServiceInstance.listar({ page_size: 100 });
      espacioOptions.value = data.results ?? data;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los espacios.'), 'error');
    }
  };

  const loadData = () => Promise.all([loadEquipos(), loadStats(), loadEspacios()]);

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };

  const openCreate = () => {
    editingEquipo.value = null;
    resetForm();
    modalOpen.value = true;
  };

  const openEdit = (equipo) => {
    editingEquipo.value = equipo;
    resetForm();
    Object.assign(form, {
      espacio: equipo.espacio ?? '',
      codigo: equipo.codigo,
      numero_serie: equipo.numero_serie,
      numero_mac: equipo.numero_mac ?? '',
      tipo_equipo: equipo.tipo_equipo,
      marca: equipo.marca,
      modelo: equipo.modelo,
      modo_adquisicion: equipo.modo_adquisicion,
      fecha_adquisicion: equipo.fecha_adquisicion,
      fecha_renovacion: equipo.fecha_renovacion ?? '',
      estado: equipo.estado,
      responsable_usuario: equipo.responsable_usuario ?? '',
    });
    modalOpen.value = true;
  };

  const closeModal = () => {
    modalOpen.value = false;
    editingEquipo.value = null;
    resetForm();
  };

  const validateForm = () => {
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
    if (!form.codigo.trim()) formErrors.codigo = 'Ingresa el código interno.';
    if (!form.numero_serie.trim()) formErrors.numero_serie = 'Ingresa el número de serie.';
    if (!form.tipo_equipo) formErrors.tipo_equipo = 'Selecciona el tipo de equipo.';
    if (!form.marca.trim()) formErrors.marca = 'Ingresa la marca.';
    if (!form.modelo.trim()) formErrors.modelo = 'Ingresa el modelo.';
    if (!form.modo_adquisicion) formErrors.modo_adquisicion = 'Selecciona el modo de adquisición.';
    if (!form.fecha_adquisicion) formErrors.fecha_adquisicion = 'Ingresa la fecha de adquisición.';
    if (!form.estado) formErrors.estado = 'Selecciona el estado.';
    return Object.keys(formErrors).length === 0;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;

    const payload = {
      ...form,
      espacio: form.espacio || null,
      fecha_renovacion: form.fecha_renovacion || null,
    };

    try {
      if (isEditing.value) {
        await service.actualizar(editingEquipo.value.id, payload);
        showToast('Equipo actualizado correctamente.');
      } else {
        await service.crear(payload);
        showToast('Equipo registrado correctamente.');
      }
      closeModal();
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo guardar el equipo.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDelete = (equipo) => {
    pendingDelete.value = equipo;
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
      showToast('Equipo retirado correctamente.');
      cancelDelete();
      await loadData();
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo retirar el equipo.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const applyFilters = () => {
    filters.page = 1;
    return loadEquipos();
  };

  const clearFilters = () => {
    Object.assign(filters, { search: '', tipo_equipo: '', estado: '', page: 1 });
    return loadEquipos();
  };

  const changePage = (page) => {
    filters.page = page;
    return loadEquipos();
  };

  const showToast = (message, type = 'success') => {
    Object.assign(toast, { show: true, message, type });
  };

  const closeToast = () => {
    toast.show = false;
  };

  onMounted(loadData);

  return {
    equipos,
    loading,
    saving,
    modalOpen,
    deleteModalOpen,
    editingEquipo,
    pendingDelete,
    form,
    formErrors,
    filters,
    pagination,
    stats,
    toast,
    isEditing,
    canManageAll,
    tipoEquipoOptions,
    modoAdquisicionOptions,
    estadoOptions,
    espacioSelectOptions,
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
