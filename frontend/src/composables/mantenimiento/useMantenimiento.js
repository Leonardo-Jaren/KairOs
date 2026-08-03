import { computed, onMounted, reactive, ref } from 'vue';

import equiposService from '@/services/equipos.service';
import mantenimientoService from '@/services/mantenimiento.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  equipo_id: '',
  fecha: '',
  tipo_mantenimiento: 'preventivo',
  estado: 'pendiente',
  descripcion: '',
  tecnico_id: '',
});

export function useMantenimiento(
  service = mantenimientoService,
  equiposServiceInstance = equiposService,
) {
  const authStore = useAuthStore();
  const mantenimientos = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const modalOpen = ref(false);
  const deleteModalOpen = ref(false);
  const editingTicket = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const formErrors = reactive({});
  const toast = reactive({ show: false, message: '', type: 'success' });
  const filters = reactive({ search: '', estado: '', tipo_mantenimiento: '', page: 1, page_size: 8 });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const stats = reactive({
    total: 0,
    pendientes: 0,
    en_proceso: 0,
    resueltos: 0,
    cancelados: 0,
    total_tecnicos: 0,
    total_dispositivos: 0,
  });
  const equipoOptions = ref([]);
  const tecnicoOptions = ref([]);

  const isEditing = computed(() => Boolean(editingTicket.value));
  const canDelete = computed(() => authStore.user?.rol === 'admin');

  const tipoOptions = [
    { value: 'preventivo', label: 'Preventivo' },
    { value: 'correctivo', label: 'Correctivo' },
  ];

  const estadoOptions = [
    { value: 'pendiente', label: 'Pendiente' },
    { value: 'en_proceso', label: 'En mantenimiento' },
    { value: 'resuelto', label: 'Terminado' },
    { value: 'cancelado', label: 'Fuera de servicio' },
  ];

  const equipoSelectOptions = computed(() => equipoOptions.value.map((equipo) => ({
    value: equipo.id,
    label: `${equipo.codigo} · ${equipo.marca} ${equipo.modelo}`,
  })));

  const tecnicoSelectOptions = computed(() => tecnicoOptions.value.map((tecnico) => ({
    value: tecnico.id,
    label: `${tecnico.nombre_completo} (${tecnico.area})`,
  })));

  const loadMantenimientos = async () => {
    loading.value = true;
    try {
      const data = await service.listar(filters);
      mantenimientos.value = data.results ?? data;
      pagination.total = data.count ?? mantenimientos.value.length;
      pagination.totalPages = Math.max(1, Math.ceil(pagination.total / filters.page_size));
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los mantenimientos.'), 'error');
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
      const [equipos, tecnicos] = await Promise.all([
        equiposServiceInstance.obtenerOpciones(),
        service.obtenerTecnicosDisponibles(),
      ]);
      equipoOptions.value = equipos;
      tecnicoOptions.value = tecnicos;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar equipos y tecnicos.'), 'error');
    }
  };

  const loadData = () => Promise.all([loadMantenimientos(), loadStats(), loadOpciones()]);

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };

  const openCreate = () => {
    editingTicket.value = null;
    resetForm();
    modalOpen.value = true;
  };

  const openEdit = (ticket) => {
    editingTicket.value = ticket;
    resetForm();
    Object.assign(form, {
      equipo_id: ticket.equipo?.id ?? '',
      fecha: ticket.fecha,
      tipo_mantenimiento: ticket.tipo_mantenimiento,
      estado: ticket.estado,
      descripcion: ticket.descripcion,
      tecnico_id: ticket.tecnicos?.[0]?.id ?? '',
    });
    modalOpen.value = true;
  };

  const closeModal = () => {
    modalOpen.value = false;
    editingTicket.value = null;
    resetForm();
  };

  const validateForm = () => {
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
    if (!form.equipo_id) formErrors.equipo_id = 'Selecciona un equipo.';
    if (!form.fecha) formErrors.fecha = 'Ingresa la fecha del ticket.';
    if (!form.tipo_mantenimiento) formErrors.tipo_mantenimiento = 'Selecciona el tipo de mantenimiento.';
    if (!form.estado) formErrors.estado = 'Selecciona el estado.';
    if (!form.descripcion.trim()) formErrors.descripcion = 'Describe el problema o la actividad realizada.';
    return Object.keys(formErrors).length === 0;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;

    const payload = {
      equipo_id: Number(form.equipo_id),
      fecha: form.fecha,
      tipo_mantenimiento: form.tipo_mantenimiento,
      estado: form.estado,
      descripcion: form.descripcion.trim(),
      tecnicos_ids: form.tecnico_id ? [Number(form.tecnico_id)] : [],
    };

    try {
      if (isEditing.value) {
        await service.actualizar(editingTicket.value.id, payload);
        showToast('Mantenimiento actualizado correctamente.');
      } else {
        await service.crear(payload);
        showToast('Mantenimiento registrado correctamente.');
      }
      closeModal();
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo guardar el mantenimiento.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDelete = (ticket) => {
    pendingDelete.value = ticket;
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
      showToast('Mantenimiento eliminado correctamente.');
      cancelDelete();
      await loadData();
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo eliminar el mantenimiento.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const applyFilters = () => {
    filters.page = 1;
    return loadMantenimientos();
  };

  const clearFilters = () => {
    Object.assign(filters, { search: '', estado: '', tipo_mantenimiento: '', page: 1 });
    return loadMantenimientos();
  };

  const changePage = (page) => {
    filters.page = page;
    return loadMantenimientos();
  };

  const showToast = (message, type = 'success') => {
    Object.assign(toast, { show: true, message, type });
  };

  const closeToast = () => {
    toast.show = false;
  };

  onMounted(loadData);

  return {
    mantenimientos,
    loading,
    saving,
    modalOpen,
    deleteModalOpen,
    editingTicket,
    pendingDelete,
    form,
    formErrors,
    filters,
    pagination,
    stats,
    toast,
    isEditing,
    canDelete,
    tipoOptions,
    estadoOptions,
    equipoSelectOptions,
    tecnicoSelectOptions,
    loadMantenimientos,
    loadStats,
    loadOpciones,
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
