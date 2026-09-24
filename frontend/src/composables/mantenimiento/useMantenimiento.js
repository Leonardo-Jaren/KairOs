import { computed, onMounted, reactive, ref } from 'vue';

import equiposService from '@/services/equipos.service';
import mantenimientoService from '@/services/mantenimiento.service';
import { useAutoFilters } from '@/composables/shared/useAutoFilters';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  equipo_id: '',
  incidencia_id: '',
  fecha: '',
  tipo_mantenimiento: 'preventivo',
  estado: 'pendiente',
  descripcion: '',
  tecnico_id: '',
  diagnostico: '',
  trabajo_realizado: '',
  resultado_equipo: '',
});

const emptyFinalizeForm = () => ({
  diagnostico: '',
  trabajo_realizado: '',
  prueba_realizada: false,
  observacion_prueba: '',
  resultado_equipo: '',
});

export function useMantenimiento(
  service = mantenimientoService,
  equiposServiceInstance = equiposService,
) {
  const authStore = useAuthStore();
  const mantenimientos = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const finalizing = ref(false);
  const modalOpen = ref(false);
  const finalizeModalOpen = ref(false);
  const detailOpen = ref(false);
  const deleteModalOpen = ref(false);
  const editingTicket = ref(null);
  const finalizingTicket = ref(null);
  const selectedTicket = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const finalizeForm = reactive(emptyFinalizeForm());
  const formErrors = reactive({});
  const finalizeErrors = reactive({});
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
  const canCreate = computed(() => authStore.hasPermission('mantenimiento', 'crear'));
  const canEdit = computed(() => authStore.hasPermission('mantenimiento', 'editar'));
  const canDeleteEffective = computed(() => authStore.hasPermission('mantenimiento', 'eliminar'));
  const canDelete = canDeleteEffective;

  const tipoOptions = [
    { value: 'preventivo', label: 'Preventivo' },
    { value: 'correctivo', label: 'Correctivo' },
  ];

  const estadoOptions = [
    { value: 'pendiente', label: 'Pendiente' },
    { value: 'en_proceso', label: 'En atención' },
    { value: 'resuelto', label: 'Finalizado' },
    { value: 'cancelado', label: 'Cancelado' },
  ];

  const estadoEdicionOptions = [
    { value: 'pendiente', label: 'Pendiente' },
    { value: 'en_proceso', label: 'En atención' },
    { value: 'cancelado', label: 'Cancelado' },
  ];

  const resultadoEquipoOptions = [
    { value: 'en_uso', label: 'En uso' },
    { value: 'en_mantenimiento', label: 'En mantenimiento' },
    { value: 'dañado', label: 'Dañado' },
    { value: 'de_baja', label: 'De baja' },
  ];

  const resultadoFinalOptions = [
    { value: 'en_uso', label: 'Funcional / en uso' },
    { value: 'dañado', label: 'Dañado' },
    { value: 'de_baja', label: 'De baja' },
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

  const resetFinalizeForm = () => {
    Object.assign(finalizeForm, emptyFinalizeForm());
    Object.keys(finalizeErrors).forEach((key) => delete finalizeErrors[key]);
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
      incidencia_id: ticket.incidencia_origen_id ?? '',
      fecha: ticket.fecha,
      tipo_mantenimiento: ticket.tipo_mantenimiento,
      estado: ticket.estado,
      descripcion: ticket.descripcion,
      tecnico_id: ticket.tecnicos?.[0]?.id ?? '',
      diagnostico: ticket.diagnostico ?? '',
      trabajo_realizado: ticket.trabajo_realizado ?? '',
      resultado_equipo: ticket.resultado_equipo ?? '',
    });
    modalOpen.value = true;
  };

  const openFinalize = (ticket) => {
    finalizingTicket.value = ticket;
    resetFinalizeForm();
    finalizeModalOpen.value = true;
  };

  const closeFinalize = () => {
    finalizeModalOpen.value = false;
    finalizingTicket.value = null;
    resetFinalizeForm();
  };

  const openDetail = (ticket) => {
    selectedTicket.value = ticket;
    detailOpen.value = true;
  };

  const closeDetail = () => {
    detailOpen.value = false;
    selectedTicket.value = null;
  };

  const startMaintenance = async (ticket) => {
    if (!ticket) return false;
    finalizing.value = true;
    try {
      await service.iniciar(ticket.id);
      showToast(`Mantenimiento #${ticket.id} en atención.`);
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo iniciar el mantenimiento.'), 'error');
      return false;
    } finally {
      finalizing.value = false;
    }
  };

  const validateFinalize = () => {
    Object.keys(finalizeErrors).forEach((key) => delete finalizeErrors[key]);
    if (!finalizeForm.diagnostico.trim()) finalizeErrors.diagnostico = 'Registra el diagnóstico.';
    if (!finalizeForm.trabajo_realizado.trim()) finalizeErrors.trabajo_realizado = 'Registra el trabajo realizado.';
    if (!finalizeForm.prueba_realizada) finalizeErrors.prueba_realizada = 'Confirma que realizaste la prueba.';
    if (!finalizeForm.resultado_equipo) finalizeErrors.resultado_equipo = 'Selecciona el resultado del equipo.';
    return Object.keys(finalizeErrors).length === 0;
  };

  const finalizeMaintenance = async () => {
    if (!validateFinalize() || !finalizingTicket.value) return false;
    finalizing.value = true;
    try {
      const result = await service.finalizar(finalizingTicket.value.id, {
        diagnostico: finalizeForm.diagnostico.trim(),
        trabajo_realizado: finalizeForm.trabajo_realizado.trim(),
        prueba_realizada: finalizeForm.prueba_realizada,
        observacion_prueba: finalizeForm.observacion_prueba.trim(),
        resultado_equipo: finalizeForm.resultado_equipo,
      });
      if (result.incidencia?.cerrada_automaticamente) {
        showToast(
          `Mantenimiento finalizado. Equipo marcado como funcional. INC-${result.incidencia.id} cerrada automáticamente.`,
        );
      } else if (result.siguiente_accion === 'crear_correctivo') {
        showToast('Mantenimiento finalizado. La incidencia requiere otra intervención.', 'error');
      } else {
        showToast('Mantenimiento finalizado correctamente.');
      }
      closeFinalize();
      await loadData();
      return result;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo finalizar el mantenimiento.'), 'error');
      return false;
    } finally {
      finalizing.value = false;
    }
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
    if (isEditing.value && form.estado === 'resuelto' && !form.diagnostico.trim()) formErrors.diagnostico = 'Registra el diagnóstico.';
    if (isEditing.value && form.estado === 'resuelto' && !form.trabajo_realizado.trim()) formErrors.trabajo_realizado = 'Registra el trabajo realizado.';
    if (isEditing.value && form.estado === 'resuelto' && !form.resultado_equipo) formErrors.resultado_equipo = 'Indica el resultado del equipo.';
    return Object.keys(formErrors).length === 0;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;

    const payload = {
      equipo_id: Number(form.equipo_id),
      incidencia_id: form.incidencia_id ? Number(form.incidencia_id) : null,
      fecha: form.fecha,
      tipo_mantenimiento: form.tipo_mantenimiento,
      estado: form.estado,
      descripcion: form.descripcion.trim(),
      tecnicos_ids: form.tecnico_id ? [Number(form.tecnico_id)] : [],
      diagnostico: form.diagnostico.trim(),
      trabajo_realizado: form.trabajo_realizado.trim(),
      resultado_equipo: form.resultado_equipo || null,
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

  const { applyFilters, resetFilters } = useAutoFilters(filters, loadMantenimientos, {
    immediateKeys: ['estado', 'tipo_mantenimiento'],
  });

  const clearFilters = () => resetFilters({ search: '', estado: '', tipo_mantenimiento: '' });

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
    finalizing,
    modalOpen,
    finalizeModalOpen,
    detailOpen,
    deleteModalOpen,
    editingTicket,
    finalizingTicket,
    selectedTicket,
    pendingDelete,
    form,
    finalizeForm,
    formErrors,
    finalizeErrors,
    filters,
    pagination,
    stats,
    toast,
    isEditing,
    canDelete,
    canCreate,
    canEdit,
    canDeleteEffective,
    tipoOptions,
    estadoOptions,
    estadoEdicionOptions,
    equipoSelectOptions,
    tecnicoSelectOptions,
    resultadoEquipoOptions,
    resultadoFinalOptions,
    loadMantenimientos,
    loadStats,
    loadOpciones,
    openCreate,
    openEdit,
    openFinalize,
    closeFinalize,
    openDetail,
    closeDetail,
    startMaintenance,
    finalizeMaintenance,
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
